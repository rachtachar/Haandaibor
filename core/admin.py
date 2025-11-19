# core/admin.py
from django.contrib import admin
from .models import User, Post, JoinRequest, ChatMessage, ProfileComment

# การลงทะเบียนแบบง่าย
admin.site.register(User)
admin.site.register(Post)
admin.site.register(JoinRequest)
admin.site.register(ChatMessage)
admin.site.register(ProfileComment)