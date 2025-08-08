import os
from celery import Celery
from django.conf import settings

# تعيين إعدادات Django للـ Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('chess_analyzer')

# تحميل الإعدادات من Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# البحث التلقائي عن المهام في جميع التطبيقات
app.autodiscover_tasks()

# مهمة اختبار
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
