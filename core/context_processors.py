# core/context_processors.py
from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        # ดึงจำนวนที่ยังไม่อ่าน
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        # ดึง 5 รายการล่าสุดมาโชว์ (เผื่อทำ dropdown)
        latest = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
        return {
            'noti_count': count,
            'latest_notis': latest
        }
    return {
        'noti_count': 0,
        'latest_notis': []
    }