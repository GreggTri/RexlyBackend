import logging
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from .jwtHandler import decodeJWT

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class jwtBearer(HTTPBearer):
    def __init__(self, auto_Error: bool = True):
        super(jwtBearer, self).__init__(auto_error=auto_Error)
    
    async def __call__(self, req: Request):
        credentials : HTTPAuthorizationCredentials = await super(jwtBearer, self).__call__(req)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid or Expired token")
            
            isTokenValid, jwtPayload = self.verify_jwt(credentials.credentials)
            
            if isTokenValid == False:
                raise HTTPException(status_code=403, detail="Invalid or Expired token")
            
            foundUser = req.app.db['users'].find_one({"_id": ObjectId(jwtPayload['user_id'])}, {"_id": 1})
            
            if foundUser:
                return credentials.credentials
            else:
                raise HTTPException(status_code=403, detail="Invalid or Expired token")
        else:
            raise HTTPException(status_code=403, detail="Invalid or Expired token")
    
    def verify_jwt(self, token: str):
        isTokenValid: bool = False # a false flag
        payload = decodeJWT(token)
        
        if payload:
            isTokenValid = True
        return isTokenValid, payload
        
        