import os
from celery import Celery

# تعيين إعدادات Django للـ Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('chess_analyzer')

# تحميل الإعدادات من Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# البحث التلقائي عن المهام
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
