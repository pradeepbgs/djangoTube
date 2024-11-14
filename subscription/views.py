from .repository import SubscriptionRepository
from utils.auth import verify_jwt
from django.views.decorators.http import require_POST,require_GET,require_http_methods
from django.views.decorators.csrf import csrf_exempt
import traceback
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from user.repository import UserRepository

# Create your views here.
@require_POST
@csrf_exempt
@verify_jwt
async def toggle_subscription(request,channelId):
    if not request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if not channelId:
        return JsonResponse({'error': 'Channel ID is required'}, status=400)
    
    try:
        subscriber = await UserRepository.getUserById(request.user.id)
        if not subscriber:
            return JsonResponse({'error': 'Subscriber not found'}, status=404)
        
        channel = await UserRepository.getUserById(channelId)
        if not channel:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        
        result = await SubscriptionRepository.toggleSubscription(subscriber, channel)
        if result == 'subscribed':
            message=  'Subscribed successfully'
        else:
            message = 'Unsubscribed successfully'

        return JsonResponse({'success': True, 'message': message}, status=200)
        
    except:
        traceback.print_exc()
        return JsonResponse({'error': 'Internal server error'}, status=500)

# get subscribed channels
@require_GET
@verify_jwt
async def get_subscribed_channels(request):
    if not request.user:
        return JsonResponse({'success':False, 'message':'unauthorized'}, status=401)

    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        subscribed_channels = await SubscriptionRepository.get_paginated_subscribed_channels(request.user,offset,limit)
        if not subscribed_channels:
            return JsonResponse({'success':True, 'data':[]}, status=200)
        
        data = [
            {
                'id': sub.channel.id,
                'name': sub.channel.username,
                'owner': {
                    'id': sub.channel.id,
                    'username': sub.channel.username,
                    'avatar': sub.channel.avatar if sub.channel.avatar else None
                },
            }
            for sub in subscribed_channels
        ]

        responseData = {
            'success': True,
            'data': data,
        }
        return JsonResponse(responseData, status=200)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid pagination parameters'}, status=400)
    except:
        print(traceback.format_exc())
        return JsonResponse({'success':False, 'message':'something went wrong'}, status=500)