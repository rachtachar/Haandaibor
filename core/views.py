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
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Report
from .forms import ReportForm, ResolveReportForm

import io
import qrcode
from promptpay import qrcode as promptpay_qrcode # หรือใช้ library promptpay ที่ลง
from django.http import HttpResponse


# ========== ส่วนจัดการโพสต์ (CRUD) ==========
class HomepageView(ListView):
    model = Post
    template_name = 'core/new_home.html'
    context_object_name = 'posts'
    ordering = ['-created_at'] # เรียงโพสต์ใหม่สุดขึ้นก่อน

class PostListView(ListView):
    model = Post
    template_name = 'core/post_list.html'
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
    success_url = reverse_lazy('post-list') # กลับไปหน้าแรกหลังสร้างสำเร็จ

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.owner or self.request.user.is_superuser or self.request.user.is_staff

# ---- เพิ่ม View สำหรับลบโพสต์ ----
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post-list')
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
        # ★ 2. เพิ่มเงื่อนไขตรวจสอบว่าปาร์ตี้เต็มหรือยัง ★
        if post.members.count() >= post.member_limit:
            messages.error(request, "ไม่สามารถอนุมัติได้ เนื่องจากปาร์ตี้เต็มแล้ว!")
            return redirect('post-detail', pk=post.pk)

        join_request.status = 'APPROVED'
        post.members.add(join_request.user) # เพิ่ม user เข้ากลุ่ม members
        messages.success(request, f"อนุมัติคุณ {join_request.user.username} เข้าปาร์ตี้เรียบร้อยแล้ว")
        
    elif action == 'reject':
        join_request.status = 'REJECTED'
        messages.info(request, "ปฏิเสธคำขอแล้ว")
    
    join_request.save()
    return redirect('post-detail', pk=post.pk)

@login_required
def kick_member(request, pk, user_id):
    post = get_object_or_404(Post, pk=pk)
    user_to_kick = get_object_or_404(User, pk=user_id)

    # 1. ตรวจสอบสิทธิ์: คนเตะต้องเป็นเจ้าของโพสต์เท่านั้น
    if request.user != post.owner:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เตะสมาชิกออกจากกลุ่มนี้")

    # 2. ลบออกจากสมาชิก (Many-to-Many field)
    post.members.remove(user_to_kick)

    # 3. (สำคัญ) ลบคำขอเข้าร่วม (JoinRequest) เดิมทิ้งด้วย
    # เพื่อให้สถานะรีเซ็ต เผื่อในอนาคตเขาอยากขอเข้าใหม่ หรือกันความสับสน
    JoinRequest.objects.filter(post=post, user=user_to_kick).delete()

    return redirect('post-detail', pk=post.pk)

# ========== ส่วนแชท ==========

# 1. หน้าห้องแชท (HTML)
class PostChatView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Post
    template_name = 'core/post_chat.html'
    context_object_name = 'post'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.owner or self.request.user in post.members.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ส่งฟอร์มเปล่าไปให้หน้าเว็บ (เผื่อจะใช้ CSRF token หรือ validate)
        context['chat_form'] = ChatMessageForm() 
        return context

# 2. API สำหรับดึงข้อความ (เรียกทุก 2 วิ)
@login_required
def get_chat_messages(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user != post.owner and request.user not in post.members.all():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    messages = ChatMessage.objects.filter(post=post).order_by('timestamp')
    
    data = []
    for msg in messages:
        data.append({
            'user': msg.user.username,
            'profile_url': msg.user.profile_picture.url if msg.user.profile_picture else '',
            'message': msg.message,
            
            # ★ ส่ง URL รูปภาพไปด้วย (ถ้ามี) ★
            'image_url': msg.image.url if msg.image else None,
            
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_me': msg.user == request.user
        })
    
    return JsonResponse({'messages': data})

# 3. API สำหรับส่งข้อความ (Save ลง Database)
@login_required
@require_POST
def send_chat_message(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user != post.owner and request.user not in post.members.all():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # รับข้อมูลทั้งข้อความและไฟล์รูปภาพ
    message_text = request.POST.get('message', '').strip()
    image_file = request.FILES.get('image')
    
    # ต้องมีอย่างใดอย่างหนึ่ง (ข้อความ หรือ รูป) ถึงจะบันทึก
    if message_text or image_file:
        ChatMessage.objects.create(
            post=post,
            user=request.user,
            message=message_text,
            image=image_file # บันทึกรูปภาพ
        )
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)


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

# 1. View สำหรับแสดงรายชื่อผู้ใช้ทั้งหมด (เฉพาะ Admin เท่านั้น)
class AdminUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'core/admin_user_list.html'
    context_object_name = 'users'
    ordering = ['-date_joined']
    paginate_by = 20  # แบ่งหน้าถ้าผู้ใช้เยอะ

    def test_func(self):
        # อนุญาตเฉพาะ Superuser หรือ Staff เท่านั้น
        return self.request.user.is_superuser or self.request.user.is_staff

# 2. ฟังก์ชันแบนผู้ใช้
@login_required
def admin_ban_user(request, pk):
    if not (request.user.is_superuser or request.user.is_staff):
        return HttpResponseForbidden()
    
    user_to_ban = get_object_or_404(User, pk=pk)
    if user_to_ban.is_superuser:
        messages.error(request, "ไม่สามารถแบน Superuser ได้!")
    else:
        user_to_ban.is_active = False
        user_to_ban.save()
        messages.success(request, f"แบนผู้ใช้ {user_to_ban.username} แล้ว")
    
    return redirect('admin-user-list')

# 3. ฟังก์ชันปลดแบน
@login_required
def admin_unban_user(request, pk):
    if not (request.user.is_superuser or request.user.is_staff):
        return HttpResponseForbidden()
    
    user_to_unban = get_object_or_404(User, pk=pk)
    user_to_unban.is_active = True
    user_to_unban.save()
    messages.success(request, f"ปลดแบนผู้ใช้ {user_to_unban.username} แล้ว")
    
    return redirect('admin-user-list')

# ========== ส่วนรายงานปัญหา ==========
class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'core/report_form.html'
    success_url = reverse_lazy('home') # ส่งเสร็จกลับหน้าแรก

    def form_valid(self, form):
        # บันทึกว่าใครเป็นคนแจ้ง (ดึงจาก user ที่ login อยู่)
        form.instance.reporter = self.request.user
        messages.success(self.request, "ขอบคุณสำหรับการแจ้งปัญหา ทีมงานจะตรวจสอบโดยเร็วที่สุด")
        return super().form_valid(form)
    
class UserReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'core/user_report_list.html'
    context_object_name = 'reports'
    paginate_by = 10

    def get_queryset(self):
        # ดึงเฉพาะรายการที่ "ผู้ใช้ที่ล็อกอินอยู่" เป็นคนแจ้งเท่านั้น
        return Report.objects.filter(reporter=self.request.user).order_by('-created_at')
    

# 1. View สำหรับแสดงรายการแจ้งปัญหาทั้งหมด (เฉพาะ Admin)
class AdminReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    template_name = 'core/admin_report_list.html'
    context_object_name = 'reports'
    ordering = ['-created_at'] # ใหม่สุดขึ้นก่อน
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # นับจำนวนงานแต่ละสถานะส่งไปที่ Template
        context['pending_count'] = Report.objects.filter(status='PENDING').count()
        context['resolved_count'] = Report.objects.filter(status='RESOLVED').count()
        context['rejected_count'] = Report.objects.filter(status='REJECTED').count()
        return context

# 2. ฟังก์ชันอัปเดตสถานะงาน
@login_required
def admin_update_report_status(request, pk, status):
    if not (request.user.is_superuser or request.user.is_staff):
        return HttpResponseForbidden()
    
    report = get_object_or_404(Report, pk=pk)
    
    # ตรวจสอบว่าค่า status ที่ส่งมาถูกต้องไหม
    valid_statuses = dict(Report.STATUS_CHOICES).keys()
    if status in valid_statuses:
        report.status = status
        report.save()
        messages.success(request, f"อัปเดตสถานะเรื่อง '{report.title}' เรียบร้อยแล้ว")
    else:
        messages.error(request, "สถานะไม่ถูกต้อง")
    
    return redirect('admin-report-list')

class AdminResolveReportView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Report
    form_class = ResolveReportForm
    template_name = 'core/admin_resolve_report.html'
    success_url = reverse_lazy('admin-report-list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        # เมื่อบันทึกฟอร์ม จะเปลี่ยนสถานะเป็น RESOLVED ทันที
        form.instance.status = 'RESOLVED'
        messages.success(self.request, f"ปิดงาน '{form.instance.title}' เรียบร้อยแล้ว")
        return super().form_valid(form)

class ReportDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Report
    template_name = 'core/report_detail.html'
    context_object_name = 'report'

    def test_func(self):
        report = self.get_object()
        # อนุญาตถ้าเป็น Admin/Staff หรือ เป็นคนแจ้งเรื่องเอง
        return self.request.user.is_superuser or self.request.user.is_staff or self.request.user == report.reporter

# สร้าง QR Code PromptPay
@login_required
def generate_promptpay_qr(request):
    # รับค่าจาก Parameter
    pp_id = request.GET.get('id', '')
    amount = float(request.GET.get('amount', 0.00))
    
    if not pp_id:
        return HttpResponse("Please provide ID", status=400)

    # สร้าง Payload PromptPay (รองรับทั้งเบอร์มือถือและเลขบัตรประชาชน)
    # Library promptpay จะจัดการแปลง 08x เป็น 668x ให้เอง
    payload = promptpay_qrcode.generate_payload(pp_id, amount)

    # สร้างรูป QR Code
    img = qrcode.make(payload)
    
    # แปลงรูปเป็น Byte เพื่อส่งกลับไปเป็น Response (ไม่ต้องเซฟลงเครื่อง)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")