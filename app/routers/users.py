from fastapi import APIRouter, Request, status, Response
from pydantic import BaseModel


from controllers.createAccountController import createAccountController
router = APIRouter()

class user(BaseModel):
    email: str
    phoneNumber: str
    password: str


#creates the users account and should also sent a text to user tellin them that they'r eaccount has been created.
@router.post("/createAccount", response_description="Create a new user", status_code=status.HTTP_201_CREATED)
async def createUserAccount(req: Request, res: Response, user: user):
    return await createAccountController(req, res, user)
        