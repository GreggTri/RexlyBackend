from fastapi import status
from fastapi.encoders import jsonable_encoder
import traceback
import bcrypt
import datetime
from amplitude import *
import logging

logging.config.fileConfig('logging.conf', disable_existing_loggers=True)
logger = logging.getLogger(__name__)

async def createAccountController(req, res, user):
     
    #Basic forms of validation
    if(user.email is None or user.password is None):
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
    
    newUser = {
        'email': user.email,
        'password': user.password,
        'created_At': datetime.datetime.utcnow()
    }
    newUser = jsonable_encoder(newUser)
    
    #send user to the database
    response = req.app.db['users'].insert_one(newUser)        
    newUser = req.app.db['users'].find_one({'email':newUser.get('email')})
    if response.acknowledged == True:
        
        req.app.amplitude.track(BaseEvent(
            event_type='User SignUp',
            user_id=str(newUser['_id']),
            user_properties={
                'email': newUser['email']
            }
        ))
        req.app.amplitude.shutdown()
        
        logger.info("User Created Successfully")
        return "Your account has been created! Check your phone!"
    
    #if user isn't saved to the database then we go here and return error to where user came from.
    res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    logger.critical(f"{traceback.format_exc()}")
    return f"[500 Error]: Check Backend Logs"