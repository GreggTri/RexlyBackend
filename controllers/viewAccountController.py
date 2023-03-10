from fastapi import status
from fastapi.responses import JSONResponse
import traceback
from amplitude import *
import logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

async def viewAccountController(req, res, user):
    
    if(user.email is None):
        return JSONResponse(content={
                "success": False,
                "message": "Bad Request"        
            }, status_code=400)
    
    try:
        foundUser = req.app.db['users'].find_one({"email": user.email}, {"email": 1})
        
        if foundUser is not None:
            foundUser['_id'] = str(foundUser['_id']) #so it is serialiable by JSON
            
            return JSONResponse(content={
                "success": True,
                "user": foundUser        
            }, status_code=200 )
        else:
            logger.error(f"User: {user.user_id} does not exist")
            return JSONResponse(content={
                "success": False,
                "message": "User not found"        
            }, status_code=404)
            
    except Exception as e:
        logger.error(f"Something went wrong when trying to view a user:\n{traceback.format_exc()}")
        return JSONResponse(content={
                "success": False,
                "message": "Sorry, something went wrong. Please try again."        
            }, status_code=500)