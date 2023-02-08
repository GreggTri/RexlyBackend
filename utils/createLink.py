import os
from dotenv import load_dotenv
load_dotenv()

def createLink(phoneNumber):
    return f"{os.getenv('CREATE_ACCOUNT_URL')}/create-account/{phoneNumber}"