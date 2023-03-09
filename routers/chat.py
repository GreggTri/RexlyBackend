from fastapi import APIRouter, Response, Form,  Request, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from controllers.chatController import chatController

router = APIRouter()

class chatMsg(BaseModel):
    user_id: str
    message: str

#We make the response class HTMLResponse because it is something that Twilio can understand.
#more info: https://www.twilio.com/docs/voice/twiml#twilio-understands-mime-types
@router.post("/chat", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def chat(req: Request,  res: Response, chatMsg: chatMsg):
    return await chatController(req, res, chatMsg)