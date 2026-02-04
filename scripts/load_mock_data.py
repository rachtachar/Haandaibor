import random
from faker import Faker
from django.contrib.auth import get_user_model
from core.models import Post, JoinRequest, ChatMessage, ProfileComment, Report, Notification
from django.utils import timezone

# ตั้งค่า Faker ให้เป็นภาษาไทย (ถ้าต้องการภาษาอังกฤษให้ลบ 'th_TH' ออก)
fake = Faker('th_TH')
User = get_user_model()

def run():
    print("🚀 เริ่มต้นกระบวนการ Mock Data...")

    # 1. ล้างข้อมูลเก่า (Optional: เปิดคอมเมนต์ถ้าต้องการล้างข้อมูลก่อนสร้างใหม่)
    # print("🧹 กำลังล้างข้อมูลเก่า...")
    # Report.objects.all().delete()
    # Notification.objects.all().delete()
    # ChatMessage.objects.all().delete()
    # JoinRequest.objects.all().delete()
    # ProfileComment.objects.all().delete()
    # Post.objects.all().delete()
    # User.objects.exclude(is_superuser=True).delete()

    # 2. สร้าง User ตามบทบาท (Role) สมมติ
    # เราจะแบ่งเป็น 3 กลุ่ม เพื่อทดสอบ Flow ต่างๆ:
    # - Group A: Creator (เน้นสร้างปาร์ตี้)
    # - Group B: Joiner (เน้นขอเข้าร่วม)
    # - Group C: Reporter/Commenter (เน้นรายงานและคอมเมนต์)
    
    users_creators = []
    users_joiners = []
    users_reporters = []
    all_users = []

    print("👤 กำลังสร้าง Users...")
    
    # สร้าง Creator 5 คน
    for i in range(5):
        username = f'creator_{i+1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='1234', # รหัสผ่านสำหรับทุกคน
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.sentence(),
                phone_number=f'08{random.randint(10000000, 99999999)}'
            )
            users_creators.append(user)
            all_users.append(user)
        else:
            print(f"   - User {username} มีอยู่แล้ว")

    # สร้าง Joiner 5 คน
    for i in range(5):
        username = f'joiner_{i+1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='1234',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.sentence(),
                phone_number=f'08{random.randint(10000000, 99999999)}'
            )
            users_joiners.append(user)
            all_users.append(user)
        else:
            print(f"   - User {username} มีอยู่แล้ว")

    # สร้าง Reporter/General 5 คน
    for i in range(5):
        username = f'user_{i+1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='1234',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.sentence(),
                phone_number=f'08{random.randint(10000000, 99999999)}'
            )
            users_reporters.append(user)
            all_users.append(user)
        else:
             print(f"   - User {username} มีอยู่แล้ว")

    # รวม user ที่เพิ่งสร้าง หรือมีอยู่แล้วเพื่อใช้งานต่อ
    if not users_creators: users_creators = list(User.objects.filter(username__startswith='creator'))
    if not users_joiners: users_joiners = list(User.objects.filter(username__startswith='joiner'))
    if not users_reporters: users_reporters = list(User.objects.filter(username__startswith='user'))
    all_users = users_creators + users_joiners + users_reporters

    # 3. สร้าง Post (เน้นให้ Group Creator เป็นคนสร้าง)
    print("📝 กำลังสร้าง Posts...")
    categories = ['APP', 'GAME', 'MOVIE', 'MUSIC', 'PRODUCT']
    posts = []

    for creator in users_creators:
        for _ in range(3): # สร้างคนละ 3 โพสต์
            category = random.choice(categories)
            full_price = random.choice([100, 299, 450, 1200, 50])
            member_limit = random.randint(2, 5)
            
            post = Post.objects.create(
                title=f"หาร {category} - {fake.word()}",
                description=fake.text(max_nb_chars=200),
                category=category,
                member_limit=member_limit,
                full_price=full_price,
                owner=creator,
                # image='post_images/default.jpg' # (Optional) ใส่ path รูปภาพที่มีอยู่จริงถ้าต้องการ
            )
            # เจ้าของเป็นสมาชิกคนแรกเสมอ (ตาม Logic ใน models.py)
            post.members.add(creator)
            posts.append(post)

    # 4. จำลอง Flow การ Join Request (เน้นให้ Group Joiner มาขอเข้า)
    print("🤝 จำลองการขอเข้าร่วม (Join Requests)...")
    
    for joiner in users_joiners:
        # สุ่มเลือกโพสต์ที่จะขอเข้าร่วม 3 โพสต์
        target_posts = random.sample(posts, 3)
        
        for post in target_posts:
            # ตรวจสอบว่ายังไม่เต็ม
            if post.members.count() < post.member_limit:
                # สุ่มสถานะที่จะเกิดขึ้น (Approved, Pending, Rejected)
                status_choice = random.choice(['APPROVED', 'PENDING', 'REJECTED'])
                
                jr = JoinRequest.objects.create(
                    post=post,
                    user=joiner,
                    status=status_choice
                )

                if status_choice == 'APPROVED':
                    post.members.add(joiner)
                    # สร้าง Notification แจ้งเตือนว่าเข้าได้แล้ว
                    Notification.objects.create(
                        recipient=joiner,
                        sender=post.owner,
                        post=post,
                        message=f"คำขอเข้าร่วมปาร์ตี้ {post.title} ได้รับการอนุมัติแล้ว",
                        link=f"/post/{post.id}/"
                    )
                elif status_choice == 'PENDING':
                    # สร้าง Notification ถึงเจ้าของโพสต์
                    Notification.objects.create(
                        recipient=post.owner,
                        sender=joiner,
                        post=post,
                        message=f"{joiner.username} ขอเข้าร่วมปาร์ตี้ {post.title}",
                        link=f"/post/{post.id}/"
                    )

    # 5. จำลอง Chat (เฉพาะใน Post ที่มีสมาชิกมากกว่า 1 คน)
    print("💬 จำลองบทสนทนา (Chat)...")
    for post in posts:
        if post.members.count() > 1:
            members = list(post.members.all())
            for _ in range(random.randint(3, 8)): # สร้าง 3-8 ข้อความต่อห้อง
                sender = random.choice(members)
                ChatMessage.objects.create(
                    post=post,
                    user=sender,
                    message=fake.sentence()
                )

    # 6. จำลอง Profile Comments (Group Reporter ไปเม้น Group Creator)
    print("⭐ จำลอง Profile Comments...")
    for commenter in users_reporters:
        target_user = random.choice(users_creators)
        ProfileComment.objects.create(
            profile_owner=target_user,
            author=commenter,
            comment=f"เครดิตดีมากครับ ตอบไว (Auto-generated by {fake.name()})"
        )

    # 7. จำลองการ Report (Group Reporter แจ้งปัญหา)
    print("🚨 จำลองการรายงานปัญหา (Reports)...")
    report_categories = ['BUG', 'USER', 'SCAM', 'OTHER']
    for reporter in users_reporters:
        Report.objects.create(
            reporter=reporter,
            title=f"แจ้งปัญหา {fake.word()}",
            description=fake.paragraph(),
            category=random.choice(report_categories),
            status='PENDING'
        )

    print("✅ สร้าง Mock Data เสร็จสมบูรณ์!")
    print(f"   - Users Created: {len(all_users)}")
    print(f"   - Posts Created: {len(posts)}")
    print("   - รหัสผ่านสำหรับ User ทุกคนคือ: 1234")