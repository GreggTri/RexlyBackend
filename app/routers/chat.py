from fastapi import APIRouter, Response, Request, status
from pydantic import BaseModel
from controllers.chatController import chatController

router = APIRouter()

#this is a model schema for what the incoming request will look like
class Event(BaseModel):
    Body: str
    From: str

#TODO:: Finish marketing Website and styling for create Account
#TODO:: deploy staged version of it to AWS
#TODO:: Test Webhook stuff
#TODO:: TEST & make bot a little betteer 
#TODO:: SEND INTO PRODUCTION!!!!!!!!!!!!

@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(req: Request, res: Response, incomingMsg: Event):
    return await chatController(req, res, incomingMsg)