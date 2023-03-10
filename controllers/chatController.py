from fastapi import status, Request, Response
from fastapi.responses import JSONResponse
import traceback
from twilio.twiml.messaging_response import MessagingResponse, Message
from amplitude import *
import datetime
from AI.botRunner import rexlyBot
import logging

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# req holds all the twilio info being sent, find out more here:
# https://www.twilio.com/docs/messaging/guides/webhook-request#parameters-in-twilios-request-to-your-application
async def chatController(req: Request, res: Response, chatMsg):
    #check if user has an account if not send create account link
    try:

        if chatMsg.email is None or chatMsg.message is None:
             return JSONResponse(content={
                "success": False,
                "message": "Bad Request"      
            }, status_code=400)
        
        #sends msg to Rexly
        botResponse = await rexlyBot(chatMsg.message)
        
        #this is to check if we got an error from walmart search
        if botResponse.get('search') == False:
            return JSONResponse(content={
                "success": False,
                "message": "Sorry friend, I ran into an error when looking for this product. If this issue persists please contact us at support@rexly.co"      
            }, status_code=500)
        
        #formatts response for text
        if "search" in botResponse:
            if len(botResponse.get('search')) == 0:
                botMessage = "Sorry, I couldn't find any products that fit your search"
            else:
                #this is the proper response wanted for searching products
                botMessage = f"{botResponse.get('intentResult')}"
        else:
            botMessage = str(botResponse.get('intentResult'))
        
        user = req.app.db['users'].find_one({"email": chatMsg.email}, {"_id": 1})
        #creates doc to send to DB, if products were searched for saves those products else does not
        if botResponse.get('search', {}) is not None:
            msgDoc = {
                "user_id": user['_id'],
                "user_msg": chatMsg.message,
                "tag": botResponse.get('tag'),
                "bot_response": botMessage,
                "products_recommended": botResponse.get('search', {}),
                "probability_response": botResponse.get('probRes'),
                'created_At': datetime.datetime.utcnow()
            }
        else:
            msgDoc = {
                "user_id": user['_id'],
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
                user_id=str(chatMsg.email),
                event_properties={
                    'botIntent': botResponse.get('tag'),
                }
            ))
            req.app.amplitude.shutdown()
            
            return JSONResponse(content={
                "success": True,
                "botMessage": botMessage,
                "products": botResponse.get('search', {})      
            }, status_code=200 )
            
        else:
            logger.error("Message did not get saved in the database and it was not tracked by amp")
            return JSONResponse(content={
                "success": False,
                "message": "DB did not acknowledge the request and event wasn't tracked"      
            }, status_code=500)
    
    except Exception as e:
        logger.critical(f"\n[Error]: {e}, {traceback.format_exc()}")
        return JSONResponse(content={
                "success": False,
                "message": "Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co"      
        }, status_code=500)