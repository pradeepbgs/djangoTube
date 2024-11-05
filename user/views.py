from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from utils.cloudinary import upload_image
from utils.jwt import generate_token
User = get_user_model()

# Create your views here.
@csrf_exempt
async def register_user(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            username = request.POST.get('username')
            fullname = request.POST.get('fullname')
            password = request.POST.get('password')
            avatar = request.FILES.get('avatar')
            coverImage = request.FILES.get('coverImage')

            if not email:
                return JsonResponse({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not username:
                return JsonResponse({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not fullname:
                return JsonResponse({'error': 'fullname is required'}, status=status.HTTP_400_BAD_REQUEST)
            if len(password) < 5:
                return JsonResponse({'success': False, 'error': 'Password must be at least 5 characters long'}, status=status.HTTP_400_BAD_REQUEST)

            username_exists = await sync_to_async(User.objects.filter(username=username).exists)()
            if username_exists:
                return JsonResponse({'success': False, 'error': 'Username already exists, try a unique username'}, status=status.HTTP_400_BAD_REQUEST)

        
            email_exists = await sync_to_async(User.objects.filter(email=email).exists)()
            if email_exists:
                return JsonResponse({'success': False, 'error': 'Email already exists!'}, status=status.HTTP_400_BAD_REQUEST)

            user = await sync_to_async(User.objects.create_user)(
                    username=username,
                    email=email,
                    password=password,
                    fullname=fullname,
            )
            avatar_url = None
            if avatar:
                res = await upload_image(avatar)
                avatar_url = res.get('secure_url')
            
            coverImage_url = None
            if coverImage:
                res = await upload_image(coverImage)
                coverImage_url = res.get('secure_url')
            
            user.avatat = avatar_url
            user.coverImage = coverImage_url
            await sync_to_async(user.save)()
            if user:
                return JsonResponse({'success': True, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Something went wrong : {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'success':False,'message':'Method not allowd'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

# login 

@csrf_exempt
async def login_user(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username:
            return JsonResponse({'success':False,'error':'plss give username'},status=400)
        
        if not password:
            return JsonResponse({'success':False,'error': 'Please provide a password'}, status=400)

        user = await sync_to_async(authenticate)(username=username,password=password)

        if user is not  None:
            token = await sync_to_async(generate_token)(user)
            response = JsonResponse({'success': True, 'message': 'Login successful'})
            response.set_cookie(
                key='token', 
                value=token, 
                httponly=True,
                secure=True,
                )
            return response
        else:
            return JsonResponse({'success': False, 'error': 'Invalid username or password'}, status=401)
        
    else:
        return JsonResponse({'success':False,'message':'Method not allowd'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
