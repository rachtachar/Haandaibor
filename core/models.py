# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. ข้อมูลผู้ใช้
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
    
    # [ลบออก] ไม่ต้องเก็บค่านี้ใน DB แล้ว เพราะจะคำนวณสดๆ แทน
    # divided_price = models.DecimalField(max_digits=10, decimal_places=2) 
    
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_posts')
    members = models.ManyToManyField(User, related_name='joined_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def divided_price(self):
        """
        คำนวณราคาหารตามจำนวนคนที่รับได้: ราคาเต็ม / จำนวนคนสูงสุด (member_limit)
        """
        # ป้องกันการหารด้วย 0
        if self.member_limit > 0:
            return round(self.full_price / self.member_limit, 2)
        return self.full_price
    def save(self, *args, **kwargs):
        # ตรวจสอบว่าเป็นโพสต์ที่สร้างใหม่หรือไม่ (ยังไม่มี ID)
        is_new = self.pk is None 
        
        # บันทึกข้อมูลโพสต์ลงฐานข้อมูลก่อน (เพื่อให้มี ID สำหรับสร้างความสัมพันธ์)
        super().save(*args, **kwargs)
        
        # ถ้าเป็นโพสต์ใหม่ ให้เพิ่ม owner เข้าไปใน members ทันที
        if is_new and self.owner:
            self.members.add(self.owner)
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