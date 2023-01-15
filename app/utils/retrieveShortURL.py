from .shortenedUrlLetters import shortenedUrlLetters
from fastapi.encoders import jsonable_encoder
import os
from dotenv import load_dotenv

def retrieveShortURL(req, long_url):
    #url_received = request.form["nm"]
    found_url = req.app.db({"long":long_url}) #how to actually write a query here

    if found_url:
        return f"{os.getenv('URL_DEV_LINK')}{found_url.short}"
    else:
        short_url = shortenedUrlLetters(req)
        newURL = {
            "long": long_url,
            "short": short_url
        }
        newURL = jsonable_encoder(newURL)
        response = req.app.db['urls'].insert_one(newURL)
        
        if response.acknowledged == True:
            return f"{os.getenv('URL_DEV_LINK')}{short_url}"
        else:
            return "Sorry, couldn't get the link"