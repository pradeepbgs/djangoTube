from django.db import models
from django.conf import settings
# Create your models here.

class SubscriptionModel(models.Model):
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    channel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.subscriber} subscribed to {self.channel}'

    class Meta:
        unique_together = ('subscriber', 'channel')
        indexes = [
        models.Index(fields=['created_at']),
        ]