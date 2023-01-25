from fastapi import APIRouter, Response, Request, status
from pydantic import BaseModel
from controllers.chatController import chatController

router = APIRouter()

@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(req: Request, res: Response):
    return await chatController(req, res)