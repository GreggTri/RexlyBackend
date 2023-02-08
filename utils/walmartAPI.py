import os
import traceback
import logging
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import base64
import httpx
import datetime

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
def generateWalmartHeaders():

    hashList = {
        "WM_CONSUMER.ID": os.getenv('CONSUMER_ID'),
        "WM_CONSUMER.INTIMESTAMP": str(int(datetime.datetime.now().timestamp() * 1000)),
        "WM_SEC.KEY_VERSION": "1"
    }

    try:
        sortedHashString = f"{hashList['WM_CONSUMER.ID']}\n{hashList['WM_CONSUMER.INTIMESTAMP']}\n{hashList['WM_SEC.KEY_VERSION']}\n"
        hash_obj = SHA256.new(sortedHashString.encode())
        
        privateKey = RSA.import_key(os.getenv('RSA_PRIVATE_KEY'))
        signer = pkcs1_15.new(privateKey)
        
        signature = signer.sign(hash_obj)
        signature_enc = base64.b64encode(signature).decode()
        
        #logger.info(privateKey)
        logger.info(os.getenv('RSA_PRIVATE_KEY'))
        return {
            "WM_SEC.AUTH_SIGNATURE": signature_enc,
            "WM_CONSUMER.INTIMESTAMP": hashList["WM_CONSUMER.INTIMESTAMP"],
            "WM_CONSUMER.ID": hashList["WM_CONSUMER.ID"],
            "WM_SEC.KEY_VERSION": hashList["WM_SEC.KEY_VERSION"]
        }
        
    except Exception as e:
        logger.critical(f"{e} {privateKey}, {os.getenv('RSA_PRIVATE_KEY')}", exc_info=True)
        return False


async def walmartAPI(url):
    try:
        if url is None:
            logger.warning("URL or METHOD not provided or are undefined")
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://developer.api.walmart.com/api-proxy/service/affil/product/v2/{url}", headers=generateWalmartHeaders())
            return response.json()
        
    except Exception as e:
       logger.critical(f"{e}", exc_info=True)