from fastapi import status
import traceback
from twilio.twiml.messaging_response import MessagingResponse

from AI.botRunner import rexlyBot
from utils.createLink import createLink

#this is a model schema for what the incoming request will look like

# incomingMsg holds 2 variables
# user_msg: string
# phoneNumber: string
async def chatController(req, res, incomingMsg):
    #check if user has an account if not send create account link
    #response = MessagingResponse()
    try:
       
        userExists = req.app.db['users'].find_one({"phoneNumber":incomingMsg.phoneNumber}, {'_id'})
        if not userExists:
            link = await createLink(incomingMsg.phoneNumber)
            #response.message(f"Hey! It seems you don't have an account yet. Here's a link to sign up! {link}")
            return f"Hey! It seems you don't have an account yet. Here's a link to sign up! {link}"
        
        #sends msg to Rexly
        botResponse = await rexlyBot(incomingMsg.user_msg)
        
        if botResponse == "400 Error":
            res.status_code = status.HTTP_400_BAD_REQUEST
            #response.message("Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
            return "[400 Error] Bad Request"
        elif botResponse == "500 Error":
            res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            #response.message("Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
            return "[400 Error] Bad Request"
            
        #formatts response for text
        if "search" in botResponse:
            #basic formatting for text message
            #response.message(f"{botResponse.intentResult} 1: {botResponse.search[0].name} - ${botResponse.search[0].salePrice}")
            #response.message(f"{botResponse.search[0].productTrackingUrl}")
            #response.message(f"2: {botResponse.search[1].name} - ${botResponse.search[1].salePrice}")
            #response.message(f"{botResponse.search[1].productTrackingUrl}")
            #response.message(f"3: {botResponse.search[2].name} - ${botResponse.search[2].salePrice}")
            #response.message(f"{botResponse.search[2].productTrackingUrl}")
            #response.message(f"4: {botResponse.search[3].name} - ${botResponse.search[3].salePrice}")
            #response.message(f"{botResponse.search[3].productTrackingUrl}")
            pass 
        elif "nbp" in botResponse:
            #response.message(f"") #finish
            pass
        
        else:
            #response.message(f"{botResponse.get('intentResult')}")
            pass
        
        #creates doc to send to DB
        msgDoc = {
            "user_id": userExists['_id'],
            "user_msg": incomingMsg.user_msg,
            "tag": botResponse.get('tag'),
            "bot_response": botResponse.get('intentResult'),
            "probability_response": botResponse.get('probRes')
        }
        
        response = req.app.db['messages'].insert_one(msgDoc)

        if response.acknowledged == True:
            return "ok"

        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f"[500 Error]: Internal Server Error"
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(e)
        #response.message(f"Sorry friend, I ran into an error. Please try again. If this issue persists please contact us at support@rexly.co")
        return f"[500 Error]: Internal Server Error"