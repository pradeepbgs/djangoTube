from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET,require_http_methods
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from asgiref.sync import sync_to_async
from utils.cloudinary import upload_image , delete_file_from_cloudinary
from utils.jwt import generateAccessToken,generateRefreshToken,verify_token
import traceback
from .repository import UserRepository
from video.repository import VideoRepository
from utils.auth import verify_jwt
import traceback
import json
from urllib.parse import unquote

# Create your views here.

async def generateAccessAndRefreshToken(user):
    try:
        access_token = await generateAccessToken(user)
        refresh_token = await generateRefreshToken(user)
        return access_token, refresh_token
    except Exception as e:
        print('something went wrong while generating access and refresh token',traceback.format_exc())
        return None

@require_POST
@csrf_exempt
async def register_user(request):
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

            username_exists = await UserRepository.getUserByUserName(username)
            if username_exists:
                return JsonResponse({'success': False, 'error': 'Username already exists, try a unique username'}, status=status.HTTP_400_BAD_REQUEST)

        
            email_exists = await UserRepository.getEmailByEmail(email)
            if email_exists:
                return JsonResponse({'success': False, 'error': 'Email already exists!'}, status=status.HTTP_400_BAD_REQUEST)

            user = await UserRepository.createUser(username,email,password,fullname)
            avatar_url = None
            if avatar:
                res = await upload_image(avatar)
                avatar_url = unquote(res.get('secure_url'))
            
            coverImage_url = None
            if coverImage:
                res = await upload_image(coverImage)
                coverImage_url = unquote(res.get('secure_url'))
            
            user.avatar = avatar_url
            user.coverImage = coverImage_url
            await UserRepository.saveUser(user)
            if user:
                return JsonResponse({'success': True, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': 'Something went wrong : {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# login 
@require_POST
@csrf_exempt
async def login_user(request):
        
        username = request.POST.get("username")
        password = request.POST.get("password")
    
        if not username:
            return JsonResponse({'success':False,'error':'plss give username'},status=400)
        
        if not password:
            return JsonResponse({'success':False,'error': 'Please provide a password'}, status=400)

        user = await sync_to_async(authenticate)(username=username,password=password)

        if user is not  None:
            accesToken,refreshToken = await generateAccessAndRefreshToken(user)
            response = JsonResponse({
                'success': True, 
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'fullname': user.fullname,
                    'avatar': user.avatar if user.avatar else None,
                    'coverImage': user.coverImage if user.coverImage else None,
                    'createdAt': user.created_at,
                    'accessToken': accesToken,
                    'refreshToken':refreshToken
                    }
                },status=200)
            response.set_cookie(
                key='accessToken', 
                value=accesToken, 
                httponly=True,
                secure=True,
                )
            response.set_cookie(
                key='refreshToken',
                value=refreshToken,
                httponly=True,
                secure=True,
                samesite='None'
            )
            return response
        else:
            return JsonResponse({'success': False, 'error': 'Invalid username or password'}, status=401)


@require_POST
@csrf_exempt
@verify_jwt
async def logout(request):

    if not request.user:
        return JsonResponse({'success': False, 'error': 'Unauthenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        response = JsonResponse({'success': True, 'message': 'Logout successful'})
        response.delete_cookie('token')
        return response
    except:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@require_GET
@verify_jwt
async def get_user(request):
    try:
        if not request.user:
            return JsonResponse({'success': False, 'error': 'Unauthenticated'}, status=404)
        user = await UserRepository.getUserById(request.user.id)
        userData = {
            'id':user.id,
            'username':user.username,
            'fullname':user.fullname,
            'avatar':user.avatar if user.avatar else None,
            'coverImage':user.coverImage if user.coverImage else None,
            # 'email':user.email,
            'createdAt':user.created_at,
        }
        if user:
            return JsonResponse({'success': True, 'user': userData})
        else:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': 'Something went wrong : {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@require_POST
@csrf_exempt
@verify_jwt
async def update_user(request):
    try:
        if not request.user:
            return JsonResponse({'success': False, 'error': 'Unauthenticated'}, status=404)
        
        username = request.POST.get('username')
        fullname = request.POST.get('fullname')
        avatar = request.FILES.get('avatar')
        coverImage = request.FILES.get('coverImage')

        user = await UserRepository.getUserById(request.user.id)
        if not user:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
        
        if username:
            user.username = username
        if fullname:
            user.fullname = fullname

        if avatar:
            oldAvatar = user.avatar
            res = await upload_image(avatar)
            avatar_url = unquote(res.get('secure_url'))
            user.avatar = avatar_url
            if oldAvatar:
                await delete_file_from_cloudinary(oldAvatar)

        if coverImage:
            oldCoverImage = user.coverImage
            res = await upload_image(coverImage)
            coverImage_url = unquote(res.get('secure_url'))
            print(coverImage_url)
            user.coverImage = coverImage_url
            if oldCoverImage:
                await delete_file_from_cloudinary(oldCoverImage)

        await sync_to_async(user.save)()
        return JsonResponse({'success': True, 'message': 'User details updated successfully'},status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': 'Something went wrong : {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@require_GET
async def getUserChannelProfile(request, username):
    try:
        if not username:
            return JsonResponse({'success': False, 'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
        user = await UserRepository.getUserByUserName(username)
        if not user:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
        
        user = {
                'id':user.id,
                'username':user.username,
                'fullname':user.fullname,
                'avatar':user.avatar if user.avatar else None,
                'coverImage':user.coverImage if user.coverImage else None,
                'subscribers_count': user.subscribers_count,
            }

        return JsonResponse({'success': True, 'data': user}, status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': 'Something went wrong : {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def refreshAccessToken(request):
    try:
        incomingRefreshToken = request.COOKIES.get('refreshToken') or request.headers.get('Authorization')

        if not incomingRefreshToken:
            return JsonResponse({'success': False, 'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        if incomingRefreshToken.startswith('Bearer '):
            incomingRefreshToken = incomingRefreshToken.split(' ')[1]

        decoded = await verify_token(incomingRefreshToken)
        
        if not decoded:
            return JsonResponse({'success': False, 'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = await UserRepository.getUserById(decoded.get('userId'))
        if not user:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
        accessToken , refreshToken = await generateAccessAndRefreshToken(user)

        response = JsonResponse(
            {
                'success': True, 
                'message': 'Access token refreshed successfully',
                'accessToken': accessToken,
                'refreshToken':refreshToken
                }, 
            status=status.HTTP_200_OK)
        response.set_cookie(
            key='accessToken',
            value=accessToken,
            httponly=True,
            secure=True,
            )
        response.set_cookie(
            key='refreshToken',
            value=refreshToken,
            httponly=True,
            secure=True,
        )
        return response
    except:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

