import time
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = os.getenv("JWT_ALGO")

# Returns the generated JWT
def token_response(token: str):
    return {
        "access_token": token
    }

# Signs the JWT payload
def signJWT(user_id: str):
    payload = {
        "user_id": user_id,
        "expiry": time.time() + 600*6*24*7
    }
    print(payload)
    
    token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGO)
    
    return token_response(token)

def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(jwt=token, key=JWT_SECRET, algorithms=[JWT_ALGO])
        return decode_token if decode_token['expiry'] >= time.time() else None
    except:
        return None