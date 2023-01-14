from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from twilio.rest import Client

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
    print("connected to database!")

except Exception as e:
    print("Error: ", e)
    
origins = [
    "http://localhost:5000",
    "http://localhost:3000"
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

@app.get('/')
async def root():
    
    message = app.twilio.messages.create(
    to="+12034828850", 
    from_="+18623754523",
    body="Hello from Python!")
    
    print(message.sid)
    
    return {'message': message}
