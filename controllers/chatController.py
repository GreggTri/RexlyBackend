from fastapi import status, Request, Response, Form
import traceback
import json
from twilio.twiml.messaging_response import MessagingResponse, Message
from amplitude import *
import datetime
from AI.botRunner import rexlyBot
from utils.createLink import createLink
from utils.retrieveShortURL import retrieveShortURL
import sys
import logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# req holds all the twilio info being sent, find out more here:
# https://www.twilio.com/docs/messaging/guides/webhook-request#parameters-in-twilios-request-to-your-application
async def chatController(req: Request, res: Response, chatMsg):
    #check if user has an account if not send create account link
    
    try:

        if chatMsg._id is None or chatMsg.message is None:
            res.status_code = status.HTTP_404_NOT_FOUND
            return "[404 Error]: Request data not found"
        
        #sends msg to Rexly
        botResponse = await rexlyBot(chatMsg.message)
        
        #this is to check if we got an error from walmart search
        if botResponse.get('search') == False:
            res.status_code = status.HTTP_200_OK
            botMessage = "Sorry friend, I ran into an error when looking for this product. If this issue persists please contact us at support@rexly.co"
            return botMessage
        
        #formatts response for text
        if "search" in botResponse:
            
            if len(botResponse.get('search')) == 0:
                botMessage = "Sorry, I couldn't find any products that fit your search"
            else:
                #this is to build the entire response for the user
                botMessage = f"{botResponse.get('intentResult')}\n"
                
                for index, product in enumerate(botResponse.get('search', {})):
                    botMessage += f"{index + 1}: {product.get('name')}\n${product.get('salePrice')}\n{retrieveShortURL(req, chatMsg._id, product.get('productTrackingUrl'))}\n" 
        #elif "nbp" in botResponse:
        #    response.message(f"")
        else:
            botMessage = str(botResponse.get('intentResult'))
        
        #creates doc to send to DB
        msgDoc = {
            "user_id": chatMsg._id,
            "user_msg": chatMsg.message,
            "tag": botResponse.get('tag'),
            "bot_response": botMessage,
            "probability_response": botResponse.get('probRes'),
            'created_At': datetime.datetime.utcnow()
        }
        
        DBresponse = req.app.db['messages'].insert_one(msgDoc)

        #this is to make sure that we don't log an event that didn't get sent to the DB
        if DBresponse.acknowledged == True:
            
            req.app.amplitude.track(BaseEvent(
                event_type='User Message',
                user_id=str(chatMsg._id),
                event_properties={
                    'botIntent': botResponse.get('tag'),
                }
            ))
            req.app.amplitude.shutdown()
            return botMessage

        logger.error("Message did not get saved in the database and it was not tracked by amp")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR #we must return 200 regardless or message won't be sent
        return botMessage
    
    except Exception as e:
        logger.critical(f"\n[Error]: {e}, {traceback.format_exc()}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR#we must return 200 regardless or message won't be sent
        botMessage = f"Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co"
        return botMessage