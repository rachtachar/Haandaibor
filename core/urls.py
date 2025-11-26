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
]