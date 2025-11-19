# core/forms.py
from django import forms
from .models import Post
from .models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post # กำหนดให้ฟอร์มนี้เชื่อมต่อกับโมเดลที่ชื่อว่า Post
        fields = ['title', 'description', 'category', 'member_limit', 'full_price', 'divided_price', 'image']


class ChatMessageForm(forms.ModelForm):
    # ใช้ widget TextInput เพื่อให้ช่องกรอกข้อมูลเป็นแถวเดียว และเพิ่ม placeholder
    message = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'พิมพ์ข้อความ...', 'class': 'w-full rounded-md border-gray-300'}),
        label="" # ไม่ต้องแสดง Label
    )
    class Meta:
        model = ChatMessage
        fields = ['message']

class ProfileCommentForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'แสดงความคิดเห็นต่อโปรไฟล์นี้...', 'rows': 3}),
        label=""
    )
    class Meta:
        model = ProfileComment
        fields = ['comment']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'phone_number', 'profile_picture']
