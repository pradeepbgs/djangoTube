from functools import wraps
from django.http import JsonResponse
import jwt
from utils.jwt import verify_token
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()

def verify_jwt(view_func):
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('accessToken') or request.headers.get('Authorization')
        
        # Extract Bearer token if present
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
        
        # Default user to None
        request.user = None
        
        if token:
            try:
                # Verify token
                payload = await verify_token(token)
                if payload:
                    user_id = payload.get('id')
                    if user_id:
                        # Fetch user asynchronously
                        user = await sync_to_async(User.objects.filter(id=user_id).first)()
                        if user:
                            request.user = user
            except jwt.ExpiredSignatureError:
                print("Token has expired")
            except jwt.InvalidTokenError:
                print("Invalid token")
            except Exception as e:
                print(f"Error verifying token: {e}")
                
        # Proceed to the view
        return await view_func(request, *args, **kwargs)

    return _wrapped_view
