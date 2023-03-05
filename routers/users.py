from fastapi import APIRouter, Request, status, Response
from pydantic import BaseModel


from controllers.createAccountController import createAccountController
from controllers.deleteAccountController import deleteAccountController
router = APIRouter()

class newUser(BaseModel):
    email: str
    phoneNumber: str
    password: str
    fromPhoneLink: bool

class user(BaseModel):
    _id: str
    email: str

#creates the users account and should also sent a text to user tellin them that they'r eaccount has been created.
@router.post("/createAccount", response_description="Create a new user", status_code=status.HTTP_201_CREATED)
async def createUserAccount(req: Request, res: Response, user: newUser):
    return await createAccountController(req, res, user)

@router.post("/deleteAccount", response_description="deletes a user", status_code=status.HTTP_201_CREATED)
async def deleteUserAccount(req: Request, res: Response, user: user):
    return await deleteAccountController(req, res, user)
        