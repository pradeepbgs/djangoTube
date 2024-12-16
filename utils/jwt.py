import jwt
import os
from datetime import datetime, timedelta
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 86400

@sync_to_async
def generateRefreshToken(data):
    payload = {
        'id': data.id,
        'username': data.username,
        'email': data.email,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    
@sync_to_async
def generateAccessToken(data):
    payload = {
        'id': data.id,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@sync_to_async
def verify_token(token):
    try:
        payload = jwt.decode(token,JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
