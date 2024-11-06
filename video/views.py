from asgiref.sync import sync_to_async
from .models import VideoModel
from comment.models import CommentModel
from django.http import JsonResponse
from django.db.models import Q,Count,BooleanField,Case,When,Value,F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import status
from django.contrib.auth.models import User
from utils.cloudinary import upload_image, upload_video_to_cloudinary
from django.views.decorators.csrf import csrf_exempt
from utils.auth import verify_jwt
import traceback
from django.shortcuts import get_object_or_404


# Create your views here.


# get all video with search/filter 
async def get_all_videos(request):
    if request.method == 'GET':
        page = request.GET.get('page',1)
        limit = int(request.GET.get('limit', 10))
        query = request.GET.get('query', None)
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_type = request.GET.get('sortType', 'desc')

        valid_sort_fields = ['created_at', 'title']
        valid_sort_types = ['asc', 'desc']

        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        if sort_type not in valid_sort_types:
            sort_type = 'desc'
        try:
            filters = Q()
            if query:
                filters &= Q(title__icontains=query)

            order_prefix = '-' if sort_type == 'desc' else ''
            order_by = f"{order_prefix}{sort_by}"

            @sync_to_async
            def  get_videos():
                return list(VideoModel.objects.filter(filters).order_by(order_by))
            
            @sync_to_async
            def get_pagination_data(videos):
                paginator = Paginator(videos,limit)
                try:
                    paginated_videos = paginator.get_page(page)
                except (EmptyPage, PageNotAnInteger):
                    paginated_videos = paginator.page(1)
                return {
                    'page_obj':paginated_videos,
                    'total': paginator.count,
                    'total_pages': paginator.num_pages
                }
            
            videos = await get_videos()
            pagination_data = await get_pagination_data(videos)
            page_obj = pagination_data['page_obj']

            # serialize data 
            data = []
            for video in page_obj:
                owner_data = await sync_to_async(lambda: {
                    "id": video.owner.id,
                    "fullname": video.owner.fullname,
                    "username": video.owner.username,
                    "avatar": video.owner.avatar if video.owner.avatar else None,
                })()
                data.append({
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "url": video.video_file,
                "views": video.views,
                "duration": video.duration,
                # "is_published": video.isPublished,
                "created_at": video.created_at,
                # "updated_at": video.updated_at,
                "owner": owner_data
                })

            return JsonResponse({
                    "success": True,
                    "message": "Videos fetched successfully.",
                    "data": data,
                    "total": pagination_data['total'],
                    "page": int(page),
                    "limit": limit,
                    "total_pages": pagination_data['total_pages']
                })
        except Exception as e:
            print(traceback.format_exc())  # Print the full error traceback for debugging
            return JsonResponse({
                    "success": False,
                    "message": "Something went wrong.",
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return JsonResponse({'success':False,'message':'Method not allowd'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

# get user videos by pagination

async def get_user_videos(req,userId):
    page = req.GET.get('page',1)
    limit = req.GET.get('limit',10)

    user = await sync_to_async(User.objects.filter(id=userId))()
    
    try:
        videos = VideoModel.objects.filter(owner=user).order_by('created-at')

        paginator = Paginator(videos,limit)
        try:
            paginated_videos = paginator.get_page(page)
        except (EmptyPage, PageNotAnInteger):
            paginated_videos = paginator.page(1)
        
        # serialize the data 
        data = [
            {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "videoFile": video.videoFile.url if video.videoFile else None,
                "thumbnail": video.thumbnail.url if video.thumbnail else None,
                "duration": video.duration,
                "views": video.views,
                "createdAt": video.created_at,
                # will do in future after defining good user model
                # "owner": {
                #     "id": user.id,
                #     "username": user.username,
                #     "fullname": user.fullname,
                #     "avatar": user.profile.avatar.url if user.profile.avatar else None,
                #     "coverImage": user.profile.cover_image.url if user.profile.cover_image else None,
                # },
            } for video in paginated_videos
        ]

        return JsonResponse({
            "success": True,
            "data": data,
            "page": page,
            "limit": limit,
            "total_pages": paginator.num_pages,
            "message": "Videos fetched successfully."
        }, status=status.HTTP_200_OK)

    except:
        return JsonResponse({
                "success": False,
                "message": "Something went wrong.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
@verify_jwt
async def upload_video(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    data = request.POST
    files = request.FILES

    title = data.get('title')
    description = data.get('description')
    thumbnail = files.get('thumbnail')
    video_file = files.get('videoFile')


    if not title or not description or not thumbnail or not video_file:
        return JsonResponse({'success': False, 'message': 'Please provide all required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        thumbnail_url = await upload_image(thumbnail)
        video_file_url = await upload_video_to_cloudinary(video_file)

        thumbnail_secure_url = thumbnail_url.get('secure_url')
        video_secure_url = video_file_url.get('secure_url')
        duration = video_file_url.get('duration')

        if not thumbnail_secure_url or not video_secure_url:
            raise ValueError("Invalid response from Cloudinary.")
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "message": "Something went wrong while uploading video & thumbnail.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    await sync_to_async(VideoModel.objects.create)(
        title=title,
        description=description,
        thumbnail=thumbnail_secure_url,
        video_file=video_secure_url,
        duration=duration,
        owner=request.user 
    )

    return JsonResponse({'success': True, 'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)



@csrf_exempt
@verify_jwt
async def get_video_details(request, videoId):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    user = request.user  # User is None if not authenticated, based on verify_jwt decorator

    try:
        # Fetch video instance asynchronously
        video = await sync_to_async(get_object_or_404)(VideoModel, pk=videoId)

        # Fetch video details with annotations for likes and subscriptions
        @sync_to_async
        def fetch_video_details(video, user):
            return VideoModel.objects.filter(id=video.id).annotate(
                like_count=Count('likes', filter=Q(likes__video=video)),
                subscribers_count=Count('owner__subscribers', filter=Q(owner__subscribers__channel=F('owner'))),
                is_liked=Case(
                    When(likes__liked_by=user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ) if user else Value(False, output_field=BooleanField()),
                is_subscribed=Case(
                    When(owner__subscriptions__subscriber=user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ) if user else Value(False, output_field=BooleanField())
            ).values(
                'id', 'title', 'description', 'thumbnail', 'video_file', 'views', 'isPublished', 'duration',
                'created_at', 'updated_at',
                'owner',
                'owner__id', 'owner__fullname', 'owner__username', 'owner__avatar',
                'like_count', 'subscribers_count', 'is_liked', 'is_subscribed'
            ).first()

        video_details = await fetch_video_details(video, user)
        
        if not video_details:
            return JsonResponse({'message': 'Video not found'}, status=404)
        
        # Fetch and paginate comments
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 10)

        @sync_to_async
        def get_video_comments():
            return CommentModel.objects.filter(video=video).order_by('created_at')

        @sync_to_async
        def get_paginated_comments(comments, limit, page):
            paginator = Paginator(comments, limit)
            try:
                paginated_comments = paginator.page(page)
            except (EmptyPage, PageNotAnInteger):
                paginated_comments = paginator.page(1)
            return paginated_comments

        comments = await get_video_comments()
        paginated_comments = await get_paginated_comments(comments, limit, page)

        # Prepare comment data
        comment_data = [
            {
                'id': comment.id,
                'comment': comment.comment,
                "username": comment.owner.username,
                'created_at': comment.created_at
            }
            for comment in paginated_comments
        ]

        video_details['comments'] = comment_data
        video_details['pagination'] = {
            'current_page': paginated_comments.number,
            'total_pages': paginated_comments.paginator.num_pages,
            'total_comments': paginated_comments.paginator.count
        }

        return JsonResponse(video_details)
    
    except VideoModel.DoesNotExist:
        return JsonResponse({'error': 'Video not found'}, status=404)
