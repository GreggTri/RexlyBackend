from fastapi import status
import traceback
from amplitude import *
import logging

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

async def deleteAccountController(req, res, user):
    
    if(user._id is None or user.email is None):
        res.status_code = status.HTTP_400_BAD_REQUEST
        return "Bad Request"
    
    deletedUser = req.app.db['users'].delete_one({'_id':user.get('_id')})
    
    if deletedUser.acknowledged == True:
        req.app.amplitude.track(BaseEvent(
            event_type='User Deleted',
            user_id=str(user['_id'])
        ))
         
        req.app.amplitude.shutdown()
        logger.info(f"User: {user['_id']} has been deleted successfully")
        res.status_code = status.HTTP_200_OK
        return "Your account has successfully been deleted"
    
    else:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error(f"Something went wrong when trying to delete user:\n{traceback.format_exc()}")
        return "Sorry, something went wrong. Please try again."
    
    