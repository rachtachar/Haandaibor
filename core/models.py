# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. ข้อมูลผู้ใช้ (ขยายความสามารถจาก User เดิมของ Django)
class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')

# 2. ข้อมูลโพสต์
class Post(models.Model):
    CATEGORY_CHOICES = [
        ('APP', 'แอพ'),
        ('GAME', 'เกม'),
        ('MOVIE', 'หนัง'),
        ('MUSIC', 'ดนตรี'),
        ('PRODUCT', 'สินค้า'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    member_limit = models.PositiveIntegerField(default=1)
    full_price = models.DecimalField(max_digits=10, decimal_places=2)
    divided_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_posts')
    members = models.ManyToManyField(User, related_name='joined_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 3. ข้อมูลคำขอเข้าร่วม
class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'รออนุมัติ'),
        ('APPROVED', 'อนุมัติแล้ว'),
        ('REJECTED', 'ถูกปฏิเสธ'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} requests to join {self.post.title}'

# 4. ข้อมูลแชท
class ChatMessage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message by {self.user.username} in {self.post.title}'

# 5. คอมเมนต์โปรไฟล์
class ProfileComment(models.Model):
    profile_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_received')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_made')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.profile_owner.username}\'s profile'