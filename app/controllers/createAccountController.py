from fastapi import status
from fastapi.encoders import jsonable_encoder
import os
import traceback
import bcrypt

async def createAccountController(req, res, user):
    try:
        if(user.email is None  or user.phoneNumber is None or user.password is None):
            res.status_code = status.HTTP_400_BAD_REQUEST
            return "[400 Error]: Bad Request"
        checkUser = req.app.db['users'].find_one(user.email)
        if checkUser != None:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return "User already exists"
        
        #We want to encrypt password for security reasons and store it in the database
        salt = bcrypt.gensalt()
        user.password = user.password.encode('utf-8')
        hashed = bcrypt.hashpw(user.password, salt)
        user.password = hashed
        
        #We want to lowercase the email
        user.email = user.email.lower()
        
        #this allows us to send the newUser to the database
        newUser = jsonable_encoder(user)
        
        #send user to the database
        response = req.app.db['users'].insert_one(newUser)        
        print(response.acknowledged)
        
        if response.acknowledged == True:
            req.app.twilio.messages.create(
                    to=user.phoneNumber, 
                    from_=os.getenv('TWILIO_NUMBER'),
                    body="your account has been created. Rexly is now at your service!"
            )
            return "ok"
        
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f"[500 Error]: Something went wrong while adding user to the database"
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        traceback.print_exc()
        
        return f"[500 Error]: {e}"