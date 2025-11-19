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
)

urlpatterns = [
    # URLs for Posts
    path('', PostListView.as_view(), name='home'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),

    # URL for Joining
    path('post/<int:pk>/join/', request_join_post, name='post-join'),
    path('request/<int:request_id>/<str:action>/', manage_join_request, name='manage-request'),

    # URL for Chat
    path('post/<int:pk>/chat/', PostChatView.as_view(), name='post-chat'),

    # URLs for Profiles
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/comment/', add_profile_comment, name='add-comment'),
]