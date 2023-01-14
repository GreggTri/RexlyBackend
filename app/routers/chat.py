from fastapi import APIRouter, Response, Request, status
from pydantic import BaseModel
from controllers.chatController import chatController

router = APIRouter()

#this is a model schema for what the incoming request will look like
class IncomingMessage(BaseModel):
    user_msg: str
    phoneNumber: str

#TODO:: Finish marketing Website and styling for create Account
#TODO:: setup git repo
#TODO:: deploy staged version of it
#TODO:: set-up twillio SMS API for chat <- CreateAccount part is done but need public server for webhook
#TODO:: TEST & make bot a little betteer 
#TODO:: SEND INTO PRODUCTION!!!!!!!!!!!!

@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(req: Request, res: Response, incomingMsg: IncomingMessage):
    return await chatController(req, res, incomingMsg)