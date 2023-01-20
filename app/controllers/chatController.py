from fastapi import status
import traceback
from twilio.twiml.messaging_response import MessagingResponse, Message
from amplitude import *
import datetime
from AI.botRunner import rexlyBot
from utils.createLink import createLink
from utils.retrieveShortURL import retrieveShortURL

#this is a model schema for what the incoming request will look like

# incomingMsg holds 2 variables
# user_msg: string
# phoneNumber: string
async def chatController(req, res, incomingMsg):
    #check if user has an account if not send create account link
    response = MessagingResponse()
    message = Message()
    try:
        
        if incomingMsg.Body is None or incomingMsg.From is None:
            res.status_code = status.HTTP_404_NOT_FOUND
            return "[404 Error]: Request data not found"
       
        userExists = req.app.db['users'].find_one({"phoneNumber":incomingMsg.From}, {'_id'})
        if not userExists:
            link = await createLink(incomingMsg.From)
            response.message(f"Hey! It seems you don't have an account yet. Here's a link to sign up! {link}")
            return f"Create Account Link Sent"
        
        #sends msg to Rexly
        botResponse = await rexlyBot(incomingMsg.Body)
        
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
            #basic formatting for text message
            message.body(f"{botResponse.get('intentResult')}")
            message.body(f" 1: {botResponse.get('search', {})[0].get('name')} - ${botResponse.get('search', {})[0].get('salePrice')}")
            #lets not do this for now to save money and see how it goes. this is for sending pictures
            #message.media(botResponse.get('search')[0].get('mediumImage'))
            message.body(await retrieveShortURL(req, userExists['_id'],botResponse.get('search')[0].get('productTrackingUrl')))
            
            message.body(f" 2: {botResponse.get('search', {})[1].get('name')} - ${botResponse.get('search', {})[1].get('salePrice')}")
            #message.media(botResponse.get('search')[0].get('mediumImage'))
            message.body(await retrieveShortURL(req, userExists['_id'], botResponse.get('search')[1].get('productTrackingUrl')))
            
            message.body(f" 3: {botResponse.get('search', {})[2].get('name')} - ${botResponse.get('search', {})[2].get('salePrice')}")
            #message.media(botResponse.get('search')[0].get('mediumImage'))
            message.body(await retrieveShortURL(req, userExists['_id'], botResponse.get('search')[2].get('productTrackingUrl')))
            
            message.body(f" 4: {botResponse.get('search', {})[3].get('name')} - ${botResponse.get('search', {})[3].get('salePrice')}")
            #message.media(botResponse.get('search')[0].get('mediumImage'))
            message.body(await retrieveShortURL(req, userExists['_id'], botResponse.get('search')[3].get('productTrackingUrl')))
            response.append(message)
        #elif "nbp" in botResponse:
        #    response.message(f"")
        else:
            response.message(f"{botResponse.get('intentResult')}")
        
        #creates doc to send to DB
        msgDoc = {
            "user_id": userExists['_id'],
            "user_msg": incomingMsg.Body,
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
            return "ok"

        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f"[500 Error]: Internal Server Error"
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(e)
        #response.message(f"Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
        return f"[500 Error]: Internal Server Error"