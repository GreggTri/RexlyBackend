from fastapi import status
from fastapi.encoders import jsonable_encoder
import traceback
import os
import bcrypt
import datetime
from amplitude import *
import logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

async def createAccountController(req, res, user):
     
    
    #Basic forms of validation
    if(user.email is None  or user.phoneNumber is None or user.password is None):
        res.status_code = status.HTTP_400_BAD_REQUEST
        return "[400 Error]: Bad Request"
    
    checkUser = req.app.db['users'].find_one({"email": user.email})
    if checkUser != None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return "[400 Error]: User already exists"
    
    #We want to encrypt password for security reasons and store it in the database
    salt = bcrypt.gensalt()
    user.password = user.password.encode('utf-8')
    hashed = bcrypt.hashpw(user.password, salt)
    user.password = hashed
    
    #We want to lowercase the email
    user.email = user.email.lower()
    
    #this allows us to send the newUser to the database
    fromPhoneLink = user.fromPhoneLink
    
    #if from phonelink it comes with "+1" if it request comes from website then id doesn't so we have to add it
    user.phoneNumber = user.phoneNumber if fromPhoneLink else '+1' + user.phoneNumber
    
    newUser = {
        'email': user.email,
        'phoneNumber': user.phoneNumber,
        'password': user.password,
        'created_At': datetime.datetime.utcnow()
    }
    
    newUser = jsonable_encoder(newUser)
    
    #send user to the database
    response = req.app.db['users'].insert_one(newUser)        
    newUser = req.app.db['users'].find_one({'email':newUser.get('email')})
    if response.acknowledged == True:
        req.app.twilio.messages.create(
                to=user.phoneNumber, 
                from_=os.getenv('TWILIO_NUMBER'),
                body="your account has been created. Rexly is now at your service! if you would like to stop using rexly, please send us an email at support@rexly.co"
        )
        
        req.app.amplitude.track(BaseEvent(
            event_type='User SignUp',
            user_id=str(newUser['_id']),
            event_properties={
                'fromPhoneLink': fromPhoneLink
            }
        ))
        
        req.app.amplitude.shutdown()
        logger.info("User Created Successfully")
        return "Your account has been created! Check your phone!"
    
    #if user isn't saved to the database then we go here and return error to where user came from.
    res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    logger.critical(f"{traceback.format_exc()}")
    return f"[500 Error]: Check Backend Logs"