from dotenv import load_dotenv
import os
import jwt
import time

load_dotenv()

SERVER_SECRET_KEY = os.getenv("SERVER_SECRET_KEY")

# print(SERVER_SECRET_KEY)

# Function generate the token
def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + 24 * 60 * 60  # expires in sec
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