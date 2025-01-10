from django.contrib import admin
from .models import DisLikeModel,LikeModel
# Register your models here.

admin.register(LikeModel)
admin.register(DisLikeModel)