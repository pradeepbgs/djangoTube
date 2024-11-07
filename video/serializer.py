from rest_framework import serializers
from comment.models import CommentModel
from .models import VideoModel
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ['id', 'comment', 'owner__username', 'created_at']  # Customize this as per your fields


class GetVideoDetailsSerializers(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True)
    pagination = serializers.SerializerMethodField()

    class Meta:
        model = VideoModel
        fields = ['id', 'title', 'description', 'thumbnail', 'video_file', 'views', 'isPublished', 'duration', 
                  'created_at', 'updated_at', 'like_count', 'subscribers_count', 'is_liked', 'is_subscribed', 'owner', 'comments', 'pagination']
        
    async def get_owner(self,obj):
        return await sync_to_async(lambda:{
            "id": obj.owner.id,
            "fullname": obj.owner.fullname,
            "username": obj.owner.username,
            "avatar": obj.owner.avatar
        })()

    async def get_pagination(self, obj):
        request = self.context.get('request')
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 10)

        # Fetch comments and paginate asynchronously
        comments = await sync_to_async(lambda: CommentModel.objects.filter(video=obj))()
        paginator = Paginator(comments, limit)
        paginated_comments = await sync_to_async(paginator.page)(page)

        return {
            'current_page': paginated_comments.number,
            'total_pages': paginated_comments.paginator.num_pages,
            'total_comments': paginated_comments.paginator.count
        }
    
