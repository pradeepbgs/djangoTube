from asgiref.sync import sync_to_async
from .models import CommentModel
import traceback
from django.db.models import Q, Count, BooleanField, Case, When, Value, F


class CommentRepository:

    @staticmethod
    @sync_to_async
    def addComment(comment,video,owner):
        try:
            return CommentModel.objects.create(comment=comment,video=video,owner=owner)
        except:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def getCommentByCommentId(commentId):
        try:
            return CommentModel.objects.get(id=commentId)
        except CommentModel.DoesNotExist:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def getVideoCommentsByVideo(video,user,offset,limit=10):
        try:
            result=  (
                 CommentModel.objects.filter(video=video)
                .select_related('owner')
                .annotate(
                    likes_count=Count('likes', filter=Q(comment=video)),
                          is_liked=Case(
                            When(likemodel__liked_by=user, then=Value(True)),
                            default=Value(False),
                            output_field=BooleanField(),
                        ) if user else Value(False, output_field=BooleanField())
                )
                .order_by('created_at')[offset:offset+limit]
            )
            return list(result) if result.exists() else None
        except CommentModel.DoesNotExist:
            return None