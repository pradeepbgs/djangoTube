from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import traceback
User = get_user_model()

class UserRepository:

    @staticmethod
    @sync_to_async
    def getUserByUserName(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            print(traceback.format_exc())
            return None

    @staticmethod
    @sync_to_async
    def getEmailByEmail(email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def createUser(username,email,password,fullname):
        try:
            return User.objects.create(
                username=username,
                email=email,
                password=password,
                fullname=fullname,
            )
        except:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def saveUser(user):
        try:
            return user.save()
        except:
            print(traceback.format_exc())
            return None