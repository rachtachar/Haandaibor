# core/urls.py
from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    ProfileUpdateView,
    request_join_post,
    manage_join_request,
    PostChatView,
    ProfileView,
    add_profile_comment,
    get_chat_messages,
    send_chat_message,
    kick_member,
    HomepageView,
    AdminUserListView,
    admin_ban_user,
    admin_unban_user,
    ReportCreateView,
    AdminReportListView,
    admin_update_report_status,
    UserReportListView,
    AdminResolveReportView,
    ReportDetailView,
    generate_promptpay_qr,
    BillCalculatorView,
    NotificationListView, 
    mark_notification_read,
    mark_all_notifications_read,
    leave_party,

)

urlpatterns = [
    # URLs for Posts
    path('', HomepageView.as_view(), name='home'),
    path('post', PostListView.as_view(), name='post-list'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),

    # URL for Joining
    path('post/<int:pk>/join/', request_join_post, name='post-join'),
    path('request/<int:request_id>/<str:action>/', manage_join_request, name='manage-request'),

    # URL for Chat
    path('post/<int:pk>/chat/', PostChatView.as_view(), name='post-chat'),
    path('post/<int:pk>/chat/api/get/', get_chat_messages, name='chat-api-get'),
    path('post/<int:pk>/chat/api/send/', send_chat_message, name='chat-api-send'),
    

    #สำหรับ Redis
    # # 1. หน้าห้องแชทหลัก
    # path('post/<int:pk>/chat/', PostChatView.as_view(), name='post-chat'),
    # # 2. API ดึงข้อความ
    # path('post/<int:pk>/chat/api/get/', get_chat_messages, name='chat-api-get'),
    # # 3. API ส่งข้อความ
    # path('post/<int:pk>/chat/api/send/', send_chat_message, name='chat-api-send'),

    # URLs for Profiles
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/comment/', add_profile_comment, name='add-comment'),

    # URL สำหรับเตะสมาชิก
    path('post/<int:pk>/kick/<int:user_id>/', kick_member, name='kick-member'),

    # URL สำหรับระบบ Admin แบบ Custom
    path('system/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('system/users/<int:pk>/ban/', admin_ban_user, name='admin-ban-user'),
    path('system/users/<int:pk>/unban/', admin_unban_user, name='admin-unban-user'),

    # URL สำหรับดูประวัติการแจ้งปัญหาของผู้ใช้เอง
    path('report/', ReportCreateView.as_view(), name='report-create'),
    path('my-reports/', UserReportListView.as_view(), name='user-report-list'),

    # URL สำหรับระบบ Admin ดูรายงานปัญหาทั้งหมด
    path('system/reports/', AdminReportListView.as_view(), name='admin-report-list'),
    path('system/reports/<int:pk>/update/<str:status>/', admin_update_report_status, name='admin-update-report'),
    path('system/reports/<int:pk>/resolve/', AdminResolveReportView.as_view(), name='admin-resolve-report'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    
    # URL สำหรับ Generate QR Code PromptPay
    path('api/generate-qr/', generate_promptpay_qr, name='generate-qr'),

    path('tools/calculator/', BillCalculatorView.as_view(), name='bill-calculator'),

    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', mark_notification_read, name='notification-read'),
    path('notifications/read-all/', mark_all_notifications_read, name='notification-read-all'),

    path('post/<int:pk>/leave/', leave_party, name='leave-party'),
]