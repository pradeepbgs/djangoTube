from asgiref.sync import sync_to_async
from .models import CommentModel
import traceback
class CommentRepository:

    @staticmethod
    @sync_to_async
    def addComment(comment,video,owner):
        try:
            return CommentModel.objects.create(comment=comment,video=video,owner=owner)
        except:
            print(traceback.format_exc())
            return None
    
    # @staticmethod
    # @sync_to_async
    # def updateComnet():
