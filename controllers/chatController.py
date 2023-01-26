from fastapi import status, Request, Response
import traceback
import json
from twilio.twiml.messaging_response import MessagingResponse, Message
from amplitude import *
import datetime
from AI.botRunner import rexlyBot
from utils.createLink import createLink
from utils.retrieveShortURL import retrieveShortURL
import logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# req holds all the twilio info being sent, find out more here:
# https://www.twilio.com/docs/messaging/guides/webhook-request#parameters-in-twilios-request-to-your-application
async def chatController(req: Request, res: Response):
    #check if user has an account if not send create account link
    response = MessagingResponse()
    message = Message()

    
    try:
        userMsg = await req.json() #turns response body to json
        #we then give then individual variables because computer was being dumb
        body = userMsg['Body'] 
        userNumber = userMsg['From']

        if body is None or userNumber is None:
            res.status_code = status.HTTP_404_NOT_FOUND
            return "[404 Error]: Request data not found"
       
        userExists = req.app.db['users'].find_one({"phoneNumber":userNumber}, {'_id'})
        if not userExists:
            link = createLink(userNumber)
            response.message(f"Hey! It seems you don't have an account yet. Here's a link to sign up! {link}")
            return str(response)
        
        #sends msg to Rexly
        botResponse = await rexlyBot(body)
        
        #this is to check if we got an error from the ReatilerIntegrations API
        if botResponse.get('search') == "400 Error":
            logger.error("Search returned 400 Error")
            res.status_code = status.HTTP_400_BAD_REQUEST
            response.message("Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
            return "[400 Error] Bad Request"
        elif botResponse.get('search') == "500 Error":
            logger.critical("Search returned 500 Error")
            res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message("Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
            return "[400 Error] Bad Request"
            
        #formatts response for text
        if "search" in botResponse:
            if len(botResponse.get('search', {})[0]) == 0:
                response.message("Sorry, I couldn't find any products that fit your search")
            else:
                #this is to build the entire response for the user
                message.body(f"{botResponse.get('intentResult')}")
                
                for i in botResponse['search']:
                    message.body(f"{i + 1}: {botResponse.get('search', {})[i].get('name')} - ${botResponse.get('search', {})[i].get('salePrice')}")
                    #lets not do this for now to save money and see how it goes. this is for sending pictures
                    #message.media(botResponse.get('search')[0].get('mediumImage'))
                    message.body(await retrieveShortURL(req, userExists['_id'],botResponse.get('search')[i].get('productTrackingUrl')))
                
                #we then put the entire response into the messaginsResponse object
                response.append(message)  
        #elif "nbp" in botResponse:
        #    response.message(f"")
        else:
            response.message(f"{botResponse.get('intentResult')}")
        
        #creates doc to send to DB
        msgDoc = {
            "user_id": userExists['_id'],
            "user_msg": body,
            "tag": botResponse.get('tag'),
            "bot_response": botResponse.get('intentResult'),
            "probability_response": botResponse.get('probRes'),
            'created_At': datetime.datetime.utcnow()
        }
        
        DBresponse = req.app.db['messages'].insert_one(msgDoc)

        #this is to make sure that we don't log an event that didn't get sent to the DB
        if DBresponse.acknowledged == True:
            
            req.app.amplitude.track(BaseEvent(
                event_type='User Message',
                user_id=str(userExists.get('_id')),
                event_properties={
                    'botIntent': botResponse.get('tag'),
                }
            ))
            req.app.amplitude.shutdown()
            return str(response)

        logger.error("Message did not get saved in the database and it was not tracked by amp")
        res.status_code = status.HTTP_200_OK #we must return 200 regardless or message won't be sent
        return str(response)
    
    except Exception as e:
        logger.critical(f"\n[Error]: {e}")
        res.status_code = status.HTTP_200_OK #we must return 200 regardless or message won't be sent
        response.message(f"Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
        return str(response)