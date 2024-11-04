import jwt
from datetime import datetime, timedelta

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 86400

def generate_token(data):
    payload = {
        'user_id': data.id,
        'username': data.username,
        'email': data.email,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token):
    try:
        payload = jwt.decode(token,JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
