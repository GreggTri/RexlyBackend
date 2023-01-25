import os

def createLink(phoneNumber):
    return f"{os.getenv('CREATE_ACCOUNT_URL')}/create-account/{phoneNumber}"