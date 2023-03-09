from fastapi.responses import JSONResponse
from bson import ObjectId
import bcrypt
import traceback
from amplitude import *
import logging

from utils.jwtHandler import signJWT

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

async def signInController(req, res, user):
    
    if(user.email is None or user.password is None):
        return JSONResponse(content={
                "success": False,
                "message": "Bad Request"        
            }, status_code=400)
    
    try:
        user.email = user.email.lower()
        
        foundUser = req.app.db['users'].find_one({"email": user.email}, {"_id": 1, "email": 1, "password": 1})
        
        if foundUser is not None:
            
            passwordIsCorrect = bcrypt.checkpw(user.password.encode('utf-8'), foundUser['password'].encode('utf-8'))
            
            if passwordIsCorrect:
                del foundUser['password'] #we do not want to pass this back to the user
                foundUser['_id'] = str(foundUser['_id']) #so it is serialiable by JSON
                
                logger.info(f"user {foundUser['email']} has been autheticated")
                return JSONResponse(content={
                "success": True,
                "token": signJWT(user.email)        
                }, status_code=200 )
            else:
                return JSONResponse(content={
                "success": False,
                "message": "Sorry, your email/password combination is incorrect. Please try again."        
                }, status_code=400 )
                
            
        else:
            logger.error(f"User: {user.user_id} was not found in database")
            return JSONResponse(content={
                "success": False,
                "message": "Sorry, your email/password combination is incorrect. Please try again."        
            }, status_code=400)
            
    except Exception as e:
        logger.error(f"Something went wrong when trying to view a user:\n{traceback.format_exc()}")
        return JSONResponse(content={
                "success": False,
                "message": "Sorry, something went wrong. Please try again."        
            }, status_code=500)