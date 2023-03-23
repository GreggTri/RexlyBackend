from fastapi import APIRouter, WebSocket, Response, Request, status, Depends, HTTPException
from pydantic import BaseModel

from controllers.chatController import chatController
from controllers.updateMessagesController import updateMessagesController
from utils.jwtBearer import jwtBearer

router = APIRouter()

class chatMsg(BaseModel):
    message: str

@router.post("/chat", dependencies=[Depends(jwtBearer())], status_code=status.HTTP_200_OK, tags=["chat"])
async def chat(req: Request,  res: Response, chatMsg: chatMsg):
    return await chatController(req, res, chatMsg)

async def get_token(socket: WebSocket):
    auth_header = socket.headers.get("Authorization")
    if auth_header:
        token = auth_header.split(" ")[1]
        return token
    else:
        raise HTTPException(status_code=403, detail="Invalid authorization header")

@router.websocket("/messagesListener")
async def messagesListener(socket: WebSocket, token = Depends(get_token)):
    await updateMessagesController(socket, token)