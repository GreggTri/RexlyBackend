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
async def chatController(req: Request, res: Response, From: str = Form(...), Body: str = Form(...)):
    #check if user has an account if not send create account link
    response = MessagingResponse()
    message = Message()
    
    try:
        userNumber = From

        if Body is None or userNumber is None:
            res.status_code = status.HTTP_404_NOT_FOUND
            return "[404 Error]: Request data not found"
       
        userExists = req.app.db['users'].find_one({"phoneNumber":userNumber}, {'_id'})
        if not userExists:
            link = createLink(userNumber)
            response.message(f"Hey! It seems you don't have an account yet. In order to use our service, you must have an account. Here's a link to sign up! {link}")
            return str(response)
        
        #sends msg to Rexly
        botResponse = await rexlyBot(Body)
        
        #this is to check if we got an error from the ReatilerIntegrations API
        if botResponse.get('search') == False:
            #logger.error("Search returned Error")
            res.status_code = status.HTTP_200_OK
            response.message("Sorry friend, I ran into an error when looking for this product. If this issue persists please contact us at support@rexly.co")
            return str(response)
        
        #formatts response for text
        if "search" in botResponse:
            #we turn search array into a json object here because we know that it's not a string
            #we don't want a string because the error handling above is sent via a string through the search attribute
            #botResponse['search'] = botResponse['search'].json()
            
            if len(botResponse.get('search')) == 0:
                response.message("Sorry, I couldn't find any products that fit your search")
            else:
                #this is to build the entire response for the user
                message.body(f"{botResponse.get('intentResult')}")
                
                for index, product in enumerate(botResponse.get('search', {})):
                    message.body(f"{index + 1}: {product.get('name')} - ${product.get('salePrice')}")
                    #lets not do this for now to save money and see how it goes. this is for sending pictures
                    #message.media(product.get('mediumImage'))
                    message.body(retrieveShortURL(req, userExists['_id'], product.get('productTrackingUrl')))
                
                #we then put the entire response into the messaginsResponse object
                response.append(message)  
        #elif "nbp" in botResponse:
        #    response.message(f"")
        else:
            response.message(f"{botResponse.get('intentResult')}")
        
        #creates doc to send to DB
        msgDoc = {
            "user_id": userExists['_id'],
            "user_msg": Body,
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
        logger.critical(f"\n[Error]: {e}, {traceback.format_exc()}")
        res.status_code = status.HTTP_200_OK #we must return 200 regardless or message won't be sent
        response.message(f"Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
        return str(response)