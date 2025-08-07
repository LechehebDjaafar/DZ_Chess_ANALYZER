from django.db import models

class Player(models.Model):
    username = models.CharField(max_length=50, unique=True, verbose_name="اسم المستخدم")
    full_name = models.CharField(max_length=100, blank=True, verbose_name="الاسم الكامل")
    country = models.CharField(max_length=2, default='DZ', verbose_name="البلد")
    current_rating = models.IntegerField(null=True, blank=True, verbose_name="التصنيف الحالي")
    avatar_url = models.URLField(blank=True, verbose_name="رابط الصورة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "لاعب"
        verbose_name_plural = "اللاعبون"
    
    def __str__(self):
        return self.username
