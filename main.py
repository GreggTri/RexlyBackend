from fastapi import FastAPI, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from twilio.rest import Client
from amplitude import *

# Your Account SID from twilio.com/console
account_sid = os.getenv('TWILIO_ACCOUNT_TOKEN')
# Your Auth Token from twilio.com/console
auth_token  = os.getenv('TWILIO_AUTH_TOKEN')

load_dotenv()
from routers import users, chat
app = FastAPI()

try:
    app.mongodb_client = MongoClient(host=os.getenv('MONGO_URL'))
    app.db = app.mongodb_client[os.getenv('DB_NAME')]
    app.twilio = Client(account_sid, auth_token)
    app.amplitude = Amplitude(os.getenv('AMP_API_KEY'))
    print("connected to database!")

except Exception as e:
    print("Error: ", e)
    
origins = [
    os.getenv('CREATE_ACCOUNT_URL'),
    os.getenv('RETAILER_API'),
    os.getenv('URL_SERVICE')
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/v1/user")
app.include_router(chat.router, prefix="/v1")

# For elb healthcheck
@app.get('/')
async def root(req: Request, res: Response):
    
    #message = app.twilio.messages.create(
    #to="+12034828850", 
    #from_=os.getenv('TWILIO_NUMBER'),
    #body="Hello from Python!")
    
    res.status_code = status.HTTP_200_OK
    return 'ok'

# so we can ignore the favicon
@app.get('/favicon.ico', status_code=204)
def ignoreFavicon():
    pass