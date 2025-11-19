# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .models import Post, User, JoinRequest, ChatMessage, ProfileComment
from .forms import PostForm, ChatMessageForm, ProfileCommentForm, ProfileUpdateForm
from django.http import HttpResponseForbidden

# ========== ส่วนจัดการโพสต์ (CRUD) ==========

class PostListView(ListView):
    model = Post
    template_name = 'core/home.html'
    context_object_name = 'posts'
    ordering = ['-created_at'] # เรียงโพสต์ใหม่สุดขึ้นก่อน

class PostDetailView(DetailView):
    model = Post
    # template_name คือ core/post_detail.html (อัตโนมัติ)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # เช็คว่า user คนนี้เคยส่งคำขอเข้าร่วมโพสต์นี้หรือยัง
            existing_request = JoinRequest.objects.filter(post=self.object, user=self.request.user).first()
            context['existing_request'] = existing_request
        # ดึงคำขอที่ยังรออนุมัติสำหรับเจ้าของโพสต์
        if self.request.user == self.object.owner:
             context['join_requests'] = JoinRequest.objects.filter(post=self.object, status='PENDING')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('home') # กลับไปหน้าแรกหลังสร้างสำเร็จ

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.owner or self.request.user.is_superuser or self.request.user.is_staff

# ---- เพิ่ม View สำหรับลบโพสต์ ----
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    # template_name คือ core/post_confirm_delete.html (อัตโนมัติ)

    def test_func(self):
        # อนุญาตให้เจ้าของโพสต์ หรือ admin ลบได้
        post = self.get_object()
        return self.request.user == post.owner or self.request.user.is_superuser or self.request.user.is_staff

# ========== ส่วนจัดการการเข้าร่วม ==========

@login_required
def request_join_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # ป้องกันไม่ให้เจ้าของโพสต์กดขอเข้าร่วมโพสต์ตัวเอง
    if post.owner == request.user:
        return redirect('post-detail', pk=post.pk)
    
    # สร้างคำขอเข้าร่วม
    JoinRequest.objects.get_or_create(post=post, user=request.user)
    return redirect('post-detail', pk=post.pk)

@login_required
def manage_join_request(request, request_id, action):
    join_request = get_object_or_404(JoinRequest, id=request_id)
    post = join_request.post

    # ตรวจสอบสิทธิ์ว่าคนที่จัดการคำขอเป็นเจ้าของโพสต์จริง
    if request.user != post.owner:
        return HttpResponseForbidden("You are not allowed to manage this request.")

    if action == 'approve':
        join_request.status = 'APPROVED'
        post.members.add(join_request.user) # เพิ่ม user เข้ากลุ่ม members
    elif action == 'reject':
        join_request.status = 'REJECTED'
    
    join_request.save()
    return redirect('post-detail', pk=post.pk)


# ========== ส่วนแชท ==========

class PostChatView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Post
    template_name = 'core/post_chat.html'
    context_object_name = 'post'

    def test_func(self):
        # อนุญาตเฉพาะเจ้าของและสมาชิกที่อนุมัติแล้วเท่านั้น
        post = self.get_object()
        return self.request.user == post.owner or self.request.user in post.members.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = ChatMessage.objects.filter(post=self.object).order_by('timestamp')
        context['chat_form'] = ChatMessageForm()
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.post = post
            message.user = request.user
            message.save()
        return redirect('post-chat', pk=post.pk)

# ========== ส่วนโปรไฟล์ผู้ใช้ ==========

class ProfileView(DetailView):
    model = User
    template_name = 'core/profile.html'
    context_object_name = 'profile_user' # เปลี่ยนชื่อ context เพื่อไม่ให้ชนกับ user ที่ login อยู่

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ดึง User object ของหน้าโปรไฟล์นี้
        profile_user = self.get_object()
        # ดึงคอมเมนต์ทั้งหมดที่โปรไฟล์นี้ได้รับ
        context['comments'] = ProfileComment.objects.filter(profile_owner=profile_user).order_by('-created_at')
        # เพิ่มฟอร์มคอมเมนต์เข้าไปใน context
        context['comment_form'] = ProfileCommentForm()
        return context
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'core/profile_edit.html' # ตั้งชื่อ template ที่จะสร้าง

    def get_success_url(self):
        # หลังจากแก้ไขสำเร็จ ให้กลับไปที่หน้าโปรไฟล์ของตัวเอง
        return reverse('profile', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        # ทำให้ View นี้แก้ไขโปรไฟล์ของคนที่ login อยู่เท่านั้น
        return self.request.user

@login_required
def add_profile_comment(request, pk):
    # ตรวจสอบว่าเป็น method POST เท่านั้น
    if request.method == 'POST':
        profile_owner = get_object_or_404(User, pk=pk)
        form = ProfileCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.profile_owner = profile_owner
            comment.author = request.user
            comment.save()
    # ไม่ว่าจะสำเร็จหรือไม่ ก็กลับไปที่หน้าโปรไฟล์เดิม
    return redirect('profile', pk=pk)


# def login_view(request):
#     # ที่นี่คุณสามารถเพิ่ม logic การ login ได้
#     # เช่น การตรวจสอบ POST request และยืนยันตัวตนผู้ใช้
#     return render(request, 'users/login.html')