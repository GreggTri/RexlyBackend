from fastapi import status
import traceback
from amplitude import *
import logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

async def viewAccountController(req, res, user):
    
    if(user._id is None or user.email is None):
        res.status_code = status.HTTP_400_BAD_REQUEST
        return "Bad Request"
    
    try:
        foundUser = req.app.db['users'].find_one({'_id': user['_id']})
        
        if foundUser is not None:
            
            logger.info(f"User: {user['_id']} has been found")
            res.status_code = status.HTTP_200_OK
            return foundUser
        else:
            logger.error(f"User: {user['_id']} does not exist")
            res.status_code = status.HTTP_404_NOT_FOUND
            return "User could not be found."
        
    except Exception as e:
        logger.error(f"Something went wrong when trying to view a user:\n{traceback.format_exc()}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return "Sorry, something went wrong. Please try again."