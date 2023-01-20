from .shortenedUrlLetters import shortenedUrlLetters
from fastapi.encoders import jsonable_encoder
import os
import datetime
from dotenv import load_dotenv

def retrieveShortURL(req, user_id, long_url):
    #url_received = request.form["nm"]
    found_url = req.app.db({"long":long_url, "user_id":user_id})

    if found_url:
        return f"{os.getenv('URL_DEV_LINK')}{found_url.short}"
    else:
        short_url = shortenedUrlLetters(req)
        newURL = {
            "user_id": user_id,
            "long": long_url,
            "short": short_url,
            'created_At': datetime.datetime.utcnow()
        }
        newURL = jsonable_encoder(newURL)
        response = req.app.db['urls'].insert_one(newURL)
        
        if response.acknowledged == True:
            return f"{os.getenv('URL_DEV_LINK')}{short_url}"
        else:
            return "Sorry, couldn't get a link"