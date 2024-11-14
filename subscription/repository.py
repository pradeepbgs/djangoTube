from .models import SubscriptionModel
import traceback
from asgiref.sync import sync_to_async

class SubscriptionRepository:

    @staticmethod
    @sync_to_async
    def toggleSubscription(subscriber, channel):
        try:
            subscription , created = SubscriptionModel.objects.get_or_create(subscriber=subscriber, channel=channel)
            if created:
                return 'subscribed'
            else:
                subscription.delete()
                return 'unsubscribed'
        except Exception as e:
            traceback.print_exc()
            return None
    
    @staticmethod
    @sync_to_async
    def get_paginated_subscribed_channels(user,offset,limit):
        try:
            channel = (SubscriptionModel.objects
                    .filter(subscriber=user)
                    .select_related('channel')
                    .order_by('created_at')[offset:offset+limit]
                )
            return channel if channel else None
        except SubscriptionModel.DoesNotExist:
            print(traceback.format_exc())
            return None