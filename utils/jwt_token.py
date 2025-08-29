from dotenv import load_dotenv
import os
import jwt
import time

load_dotenv()

SERVER_SECRET_KEY = os.getenv("SERVER_SECRET_KEY")

# print(SERVER_SECRET_KEY)

# Function generate the token
def generate_token(user_id, username, name, expires_in=360000):
    payload = {
        "user_id": user_id,
        "username": username,
        "name": name,
        "exp": int(time.time()) + expires_in  # expires in sec
    }

    token = jwt.encode(payload, SERVER_SECRET_KEY, algorithm="HS256")
    return token

# Function: validate token
def validate_token(token):
    try:
        payload = jwt.decode(token, SERVER_SECRET_KEY, algorithms=["HS256"])
        return {"valid": True, "data": payload}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}