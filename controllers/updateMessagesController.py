from fastapi import status, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
import json
from bson import ObjectId
from bson.json_util import dumps
import traceback
import threading
import logging
import asyncio

from utils.jwtHandler import decodeJWT

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class WebSocketPubSub:
    def __init__(self):
        self.connections = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        del self.connections[user_id]
    
    async def publish(self, user_id: str, message):
        connection = self.connections.get(user_id)
        if connection:
            await connection.send_json(dumps(message))
            
pubsub = WebSocketPubSub() 
            
async def updateMessagesController(socket: WebSocket, token):
    try:
        decoded_token = decodeJWT(token)
        user_id = decoded_token["user_id"]
        checkedUser = socket.app.db["users"].find_one({"_id": ObjectId(user_id)}, {"_id": 1})
        
        if checkedUser:
            await pubsub.connect(socket, user_id)
        else:
            raise HTTPException(status_code=403, detail="Invalid or Expired token")
        
        pipeline = [{"$match": {"operationType": "insert", "fullDocument.user_id": ObjectId(user_id)}}]
        changeStream = socket.app.db['messages'].watch(pipeline)
        print(changeStream)
        while True:
            loop = asyncio.get_event_loop()
            change = await loop.run_in_executor(None, changeStream.next)
            
            message = change["fullDocument"]
            del message['user_id']
            del message['tag']
            del message['probability_response']
            del message['created_At']
            #message['_id'] = str(message['_id'])
            #message['user_id'] = str(message['user_id'])
            
            await pubsub.publish(user_id, message)
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info(f"{socket} disconnected!")
        pubsub.disconnect(socket)
        
    except HTTPException:
        logger.error(f"{socket} had error and got disconnected")
        print(socket.application_state)
        if socket.application_state == "connected":
            pubsub.disconnect(socket)    