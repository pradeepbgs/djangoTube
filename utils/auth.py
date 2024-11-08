from functools import wraps
from django.http import JsonResponse
import jwt
from utils.jwt import verify_token
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
User = get_user_model()
from asgiref.sync import sync_to_async

def verify_jwt(view_func):
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('token')
        if token:
            try:
                payload = await verify_token(token)  
                if payload:
                    user_id = payload.get('user_id')

                if user_id:
                    user = await sync_to_async(User.objects.filter(id=user_id).first)()
                    if user:
                        request.user = user
                    else:
                        request.user = None
                
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid token payload'}, status=401)

            except jwt.ExpiredSignatureError:
                return JsonResponse({'success': False, 'message': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'success': False, 'message': 'Invalid token'}, status=401)
        else:
            request.user = None
        return await view_func(request, *args, **kwargs)

    return _wrapped_view
