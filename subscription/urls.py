from django.urls import path
from . import views

urlpatterns = [
    path('toggle/<int:channelId>/',views.toggle_subscription,name='toggle subscription'),
    path('subscribed-channel/', views.get_subscribed_channels, name='get subscribed channel'),
]