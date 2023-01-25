from fastapi import status
import traceback
from twilio.twiml.messaging_response import MessagingResponse, Message
from amplitude import *
import datetime
from AI.botRunner import rexlyBot
from utils.createLink import createLink
from utils.retrieveShortURL import retrieveShortURL

# req holds all the twilio info being sent, find out more here:
# https://www.twilio.com/docs/messaging/guides/webhook-request#parameters-in-twilios-request-to-your-application
async def chatController(req, res):
    #check if user has an account if not send create account link
    response = MessagingResponse()
    message = Message()
    try:
        
        if req.Body is None or req.From is None:
            res.status_code = status.HTTP_404_NOT_FOUND
            return "[404 Error]: Request data not found"
       
        userExists = req.app.db['users'].find_one({"phoneNumber":req.From}, {'_id'})
        if not userExists:
            link = await createLink(req.From)
            response.message(f"Hey! It seems you don't have an account yet. Here's a link to sign up! {link}")
            return str(response)
        
        #sends msg to Rexly
        botResponse = await rexlyBot(req.Body)
        
        if botResponse.get('search') == "400 Error":
            res.status_code = status.HTTP_400_BAD_REQUEST
            response.message("Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
            return "[400 Error] Bad Request"
        elif botResponse.get('search') == "500 Error":
            res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message("Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
            return "[400 Error] Bad Request"
            
        #formatts response for text
        if "search" in botResponse:
            if len(botResponse.get('search', {})[0]) == 0:
                response.message("Sorry, I couldn't find any products that fit your search")
            else:
                #basic formatting for text message
                message.body(f"{botResponse.get('intentResult')}")
                
                for i in botResponse['search']:
                    message.body(f"{i + 1}: {botResponse.get('search', {})[i].get('name')} - ${botResponse.get('search', {})[i].get('salePrice')}")
                    #lets not do this for now to save money and see how it goes. this is for sending pictures
                    #message.media(botResponse.get('search')[0].get('mediumImage'))
                    message.body(await retrieveShortURL(req, userExists['_id'],botResponse.get('search')[i].get('productTrackingUrl')))
                    
                response.append(message)
        #elif "nbp" in botResponse:
        #    response.message(f"")
        else:
            response.message(f"{botResponse.get('intentResult')}")
        
        #creates doc to send to DB
        msgDoc = {
            "user_id": userExists['_id'],
            "user_msg": req.Body,
            "tag": botResponse.get('tag'),
            "bot_response": botResponse.get('intentResult'),
            "probability_response": botResponse.get('probRes'),
            'created_At': datetime.datetime.utcnow()
        }
        
        response = req.app.db['messages'].insert_one(msgDoc)

        if response.acknowledged == True:
            
            req.app.amplitude.track(BaseEvent(
                event_type='User Message',
                user_id=str(userExists.get('_id')),
                event_properties={
                    'botIntent': botResponse.get('tag'),
                }
            ))
            req.app.amplitude.shutdown()
            return str(response)

        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.message(f"Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
        return str(response)
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(e)
        response.message(f"Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
        return str(response)