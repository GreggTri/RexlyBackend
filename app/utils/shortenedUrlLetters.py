import random
import string
import os

def shortenedUrlLetters(req):
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=5)
        rand_letters = "".join(rand_letters)
        short_url = req.app.db['urls'].find_one({"short": rand_letters})
        if not short_url:
            return rand_letters