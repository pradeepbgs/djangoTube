from django.urls import  path
from . import views

urlpatterns = [
    path('register/', views.register_user,name='register'),
    path('login/',views.login_user,name='login'),
    path('logout', views.logout,name='logout'),
    path('user', views.get_user, name='get user'),
    path('update', views.update_user),
    path('channel', views.getUserChannelProfile)
]