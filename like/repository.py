from .models import LikeModel
from asgiref.sync  import sync_to_async
import traceback


class LikeRepository:

    @staticmethod
    @sync_to_async
    def toggleLike(user, video):
        try:
            like_query = LikeModel.objects.filter(
                liked_by=user,
                video=video
            )
            
            if like_query.exists():
                like_query.delete()
                return 'unliked'
            else:
                LikeModel.objects.create(
                    liked_by=user,
                    video=video
                )
                return 'liked'

        except Exception:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def toggleCommentLike(user, comment):
        try:
            like_query = LikeModel.objects.filter(
                liked_by=user,
                comment=comment
            )
            
            if like_query.exists():
                like_query.delete()
                return 'unliked'
            else:
                LikeModel.objects.create(
                    liked_by=user,
                    comment=comment
                )
                return 'liked'

        except Exception:
            print(traceback.format_exc())
            return None

    @staticmethod
    @sync_to_async
    def getLikedVideos(user,offset,limit):
        try:
            liked_videos = (
                LikeModel.objects.filter(
                liked_by=user,
            )
            .select_related('video')
            .order_by('created_at')[offset:offset+limit]
            )

            return list(liked_videos) if liked_videos else None

        except Exception:
            print(traceback.format_exc())
            return None