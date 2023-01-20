from fastapi import APIRouter, Response, Request, status
from pydantic import BaseModel
from controllers.chatController import chatController

router = APIRouter()

#this is a model schema for what the incoming request will look like
class Event(BaseModel):
    Body: str
    From: str

@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(req: Request, res: Response, incomingMsg: Event):
    return await chatController(req, res, incomingMsg)