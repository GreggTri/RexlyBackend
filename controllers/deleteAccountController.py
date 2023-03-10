from fastapi import status
from fastapi.responses import JSONResponse
from bson import ObjectId
import traceback
from amplitude import *
import logging

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

async def deleteAccountController(req, res, user):
    
    if(user.email is None):
        return JSONResponse(content={
                "success": False,
                "message": "Sorry, something went wrong. Please try again."        
        }, status_code=400)
    
    try:
        deletedUser = req.app.db['users'].delete_one({'email': user.email})
        
        if deletedUser.acknowledged == True:
            req.app.amplitude.track(BaseEvent(
                event_type='User Deleted',
                user_id=user.email
            ))
            
            req.app.amplitude.shutdown()
            logger.info(f"User: {user.email} has been deleted successfully")
            return JSONResponse(content={
                    "success": True,
                    "message": "Your account has successfully been deleted"        
            }, status_code=200)
        
        else:
            logger.error(f"Something went wrong when trying to delete user:\n{traceback.format_exc()}")
            return JSONResponse(content={
                    "success": False,
                    "message": "Sorry, something went wrong. Please try again."        
            }, status_code=500)
    
    except:
        logger.critical(f"Exception caught: :\n{traceback.format_exc()}")
        return JSONResponse(content={
                "success": False,
                "message": "Sorry, something went wrong. Please try again."        
        }, status_code=500)
    
    