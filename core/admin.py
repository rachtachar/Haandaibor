# core/admin.py
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, JoinRequest, ChatMessage, ProfileComment, Report

# 1. ปรับแต่งหน้าจัดการ User (Custom User Admin)
class CustomUserAdmin(UserAdmin):
    # ฟิลด์ที่จะแสดงในหน้ารายการ (List View)
    list_display = ('username', 'email', 'phone_number', 'is_active', 'is_staff', 'date_joined')
    
    # ตัวกรองด้านขวา (Filters)
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    # ช่องค้นหา (Search) - ค้นหาได้ทั้งชื่อ, อีเมล และเบอร์โทร
    search_fields = ('username', 'email', 'phone_number')
    
    # เพิ่มฟิลด์ที่แก้ไขได้ในหน้าลึก (Detail View)
    fieldsets = UserAdmin.fieldsets + (
        ('ข้อมูลเพิ่มเติม (Custom Fields)', {
            'fields': ('bio', 'phone_number', 'profile_picture'),
        }),
    )
    
    # เพิ่ม Actions พิเศษ (เช่น ปุ่มแบนผู้ใช้หลายคนพร้อมกัน)
    actions = ['ban_users', 'unban_users']

    @admin.action(description='🚫 แบนผู้ใช้ที่เลือก (Ban Users)')
    def ban_users(self, request, queryset):
        # สั่งให้ is_active = False เพื่อไม่ให้ล็อกอินได้
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f"แบนผู้ใช้ไปแล้ว {updated_count} คน")

    @admin.action(description='✅ ปลดแบนผู้ใช้ที่เลือก (Unban Users)')
    def unban_users(self, request, queryset):
        # สั่งให้ is_active = True กลับมาใช้งานได้ปกติ
        updated_count = queryset.update(is_active=True)
        self.message_user(request, f"ปลดแบนผู้ใช้ไปแล้ว {updated_count} คน")

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'reporter', 'status', 'created_at', 'show_evidence')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'reporter__username')
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_resolved', 'mark_as_acknowledged']

    @admin.action(description='✅ ระบุว่าแก้ไขแล้ว')
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')

    @admin.action(description='👀 ระบุว่ารับเรื่องแล้ว')
    def mark_as_acknowledged(self, request, queryset):
        queryset.update(status='ACKNOWLEDGED')
    # 2. เพิ่มฟังก์ชันสำหรับแสดงรูปภาพ
    def show_evidence(self, obj):
        if obj.evidence_image:
            # แสดงรูปขนาดเล็ก (Thumbnail) สูง 50px
            return format_html('<a href="{}" target="_blank"><img src="{}" style="height: 50px; border-radius: 5px;" /></a>', obj.evidence_image.url, obj.evidence_image.url)
        return "-"
    
    show_evidence.short_description = "หลักฐาน" # ชื่อหัวข้อในตาราง

# 2. ลงทะเบียน Model เข้ากับ Admin Site
admin.site.register(User, CustomUserAdmin) # ใช้ Class ที่เราปรับแต่ง
admin.site.register(Post)
admin.site.register(JoinRequest)
admin.site.register(ChatMessage)
admin.site.register(ProfileComment)