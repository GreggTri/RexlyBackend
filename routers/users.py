from fastapi import APIRouter, Request, status, Response, Depends
from pydantic import BaseModel, Field, EmailStr


from controllers.createAccountController import createAccountController
from controllers.signInController import signInController
from controllers.viewAccountController import viewAccountController
from controllers.deleteAccountController import deleteAccountController

from utils.jwtBearer import jwtBearer
router = APIRouter()

class authUser(BaseModel):
    email: EmailStr = Field(default=None)
    password: str
    
class UserSignIn(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
class user(BaseModel):
    user_id: str


#creates the users account and should also sent a text to user tellin them that they'r eaccount has been created.
@router.post("/createAccount", response_description="Create a new user", status_code=status.HTTP_201_CREATED, tags=["user"])
async def createUserAccount(req: Request, res: Response, user: authUser):
    return await createAccountController(req, res, user)

@router.post("/signin", response_description="Signs a user in", status_code=status.HTTP_200_OK, tags=["user"])
async def signInUser(req: Request, res: Response, user: UserSignIn):
    return await signInController(req, res, user)

@router.post("/viewAccount", dependencies=[Depends(jwtBearer())], response_description="View an account", status_code=status.HTTP_200_OK, tags=["user"])
async def viewUserAccount(req: Request, res: Response, user: user):
    return await viewAccountController(req, res, user)

@router.post("/deleteAccount", dependencies=[Depends(jwtBearer())], response_description="deletes a user", status_code=status.HTTP_200_OK, tags=["user"])
async def deleteUserAccount(req: Request, res: Response, user: user):
    return await deleteAccountController(req, res, user)
        