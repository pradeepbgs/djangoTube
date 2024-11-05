from functools import wraps
from django.http import JsonResponse
import jwt
from utils.jwt import verify_token

def verify_jwt(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('token')  # Retrieve the JWT from cookies
        if token:
            try:
                payload = verify_token(token)  # Your custom verify_token function
                user_id = payload.get('user_id')

                if user_id:
                    request.user_id = user_id  # Set the user_id on the request
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid token payload'}, status=401)

            except jwt.ExpiredSignatureError:
                return JsonResponse({'success': False, 'message': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'success': False, 'message': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'success': False, 'message': 'Token not provided'}, status=401)

        # Call the original view function
        return view_func(request, *args, **kwargs)

    return _wrapped_view
