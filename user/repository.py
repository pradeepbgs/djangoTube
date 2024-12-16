from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
import traceback
from django.contrib.auth.models import User 
from django.db.models import Count,Q,F,Case,Value,Exists,BooleanField
from django.db import models
from django.db.models import OuterRef
from subscription.models import SubscriptionModel
User = get_user_model()

class UserRepository:

    @staticmethod
    @sync_to_async
    def getUserById(id):
        try:
            user = User.objects.filter(id=id).first()
            return user if user else None
        except User.DoesNotExist:
            print(traceback.format_exc())
            return None

    @staticmethod
    @sync_to_async
    def getUserByUsername(username):
        try:
            user =  User.objects.filter(username=username).first()
            return user if user else None
        except User.DoesNotExist:
            print(traceback.format_exc())
            return None

    @staticmethod
    @sync_to_async
    def getUser(username, LoggedInUser):
        try:
            user = (
            User.objects
            .filter(username=username)
            .annotate(
                subscribers_count=Count(
                    'subscribers', filter=Q(subscribers__channel=F('id'))
                ),
                is_subscribed=Value(False, output_field=BooleanField()) 
            )
            .first()
        )

            if user:
                is_subscribed = SubscriptionModel.objects.filter(
                channel=user, subscriber=LoggedInUser
            ).exists()
                user.is_subscribed = is_subscribed 

            return user if user else None

        except User.DoesNotExist:
            print(traceback.format_exc())
            return None

    @staticmethod
    @sync_to_async
    def getEmailByEmail(email):
        try:
            user= User.objects.get(email=email)
            return user if user else None
        except User.DoesNotExist:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def createUser(username,email,password,fullname):
        try:
            user =  User.objects.create(
                username=username,
                email=email,
                fullname=fullname,
            )
            user.set_password(password)
            return user
        except:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def saveUser(user):
        try:
            user =  user.save()
            return user
        except Exception as e:
            print(f"Error saving user: {e}")
            traceback.print_exc()
            return None
