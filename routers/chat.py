from fastapi import APIRouter, Response, Form,  Request, status, Depends
from pydantic import BaseModel, EmailStr, Field

from controllers.chatController import chatController
from utils.jwtBearer import jwtBearer
router = APIRouter()

class chatMsg(BaseModel):
    email:EmailStr = Field(default=None)
    message: str

#We make the response class HTMLResponse because it is something that Twilio can understand.
#more info: https://www.twilio.com/docs/voice/twiml#twilio-understands-mime-types
@router.post("/chat", dependencies=[Depends(jwtBearer())], status_code=status.HTTP_200_OK, tags=["chat"])
async def chat(req: Request,  res: Response, chatMsg: chatMsg):
    return await chatController(req, res, chatMsg)