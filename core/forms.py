# core/forms.py
from django import forms
from .models import Post
from .models import *
from .models import Report

class PostForm(forms.ModelForm):
    class Meta:
        model = Post # กำหนดให้ฟอร์มนี้เชื่อมต่อกับโมเดลที่ชื่อว่า Post
        fields = ['title', 'description', 'category', 'member_limit', 'full_price', 'image']


class ChatMessageForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'พิมพ์ข้อความ...', 'class': 'w-full rounded-md border-gray-300'}),
        label="",
        required=False # ไม่บังคับกรอก เพราะอาจจะส่งแค่รูปอย่างเดียว
    )
    
    # ★ เพิ่ม Widget สำหรับอัปโหลดรูป (ซ่อนไว้ก่อน แล้วใช้ปุ่มกดเรียก) ★
    image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'hidden', 'id': 'chat-image-input'}),
        label="",
        required=False
    )

    class Meta:
        model = ChatMessage
        fields = ['message', 'image'] # เพิ่ม image เข้าไป

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

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        # เพิ่ม 'evidence_image' เข้าไปในรายการ
        fields = ['category', 'title', 'description', 'evidence_image']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'ระบุหัวข้อเรื่องสั้นๆ', 'class': 'w-full rounded-md border-gray-300'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'อธิบายรายละเอียด...', 'class': 'w-full rounded-md border-gray-300'}),
            
            # ★ เพิ่ม Widget สำหรับปุ่มอัปโหลดไฟล์ (Tailwind Style) ★
            'evidence_image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 transition-all cursor-pointer'
            }),
        }
        labels = {
            'category': 'หมวดหมู่ปัญหา',
            'title': 'หัวข้อเรื่อง',
            'description': 'รายละเอียด',
            'evidence_image': 'รูปภาพหลักฐาน (ถ้ามี)', # Label ภาษาไทย
        }

class ResolveReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['resolution_note'] # ให้กรอกแค่รายละเอียด
        widgets = {
            'resolution_note': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'ระบุรายละเอียดการแก้ไข หรือข้อความถึงผู้แจ้งปัญหา...',
                'class': 'w-full rounded-md border-gray-300'
            }),
        }
        labels = {
            'resolution_note': 'บันทึกการแก้ไข (แจ้งให้ผู้ใช้ทราบ)',
        }
