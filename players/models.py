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

class PlayerStats(models.Model):
    """إحصاءات اللاعب الشاملة"""
    player = models.OneToOneField(Player, on_delete=models.CASCADE, verbose_name="اللاعب")
    total_games = models.IntegerField(default=0, verbose_name="إجمالي المباريات")
    wins = models.IntegerField(default=0, verbose_name="الانتصارات")
    losses = models.IntegerField(default=0, verbose_name="الهزائم")
    draws = models.IntegerField(default=0, verbose_name="التعادلات")
    favorite_opening = models.CharField(max_length=100, blank=True, verbose_name="الافتتاح المفضل")
    weakest_defense = models.CharField(max_length=100, blank=True, verbose_name="أضعف دفاع")
    average_game_length = models.IntegerField(default=0, verbose_name="متوسط طول المباراة")
    last_analysis = models.DateTimeField(null=True, blank=True, verbose_name="آخر تحليل")
    
    class Meta:
        verbose_name = "إحصاءات لاعب"
        verbose_name_plural = "إحصاءات اللاعبين"
    
    @property
    def win_percentage(self):
        """حساب نسبة الفوز"""
        if self.total_games == 0:
            return 0
        return round((self.wins / self.total_games) * 100, 1)
    
    @property
    def loss_percentage(self):
        """حساب نسبة الخسارة"""
        if self.total_games == 0:
            return 0
        return round((self.losses / self.total_games) * 100, 1)
    
    def __str__(self):
        return f"إحصاءات {self.player.username}"
class OpeningStat(models.Model):
    """إحصاءات الافتتاحات للاعب"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="اللاعب")
    opening_name = models.CharField(max_length=100, verbose_name="اسم الافتتاح")
    eco_code = models.CharField(max_length=3, verbose_name="رمز ECO")
    games_played = models.IntegerField(default=0, verbose_name="المباريات الملعوبة")
    wins = models.IntegerField(default=0, verbose_name="الانتصارات")
    losses = models.IntegerField(default=0, verbose_name="الهزائم")
    draws = models.IntegerField(default=0, verbose_name="التعادلات")
    color_played = models.CharField(
        max_length=5, 
        choices=[('white', 'أبيض'), ('black', 'أسود'), ('both', 'كلاهما')],
        default='both',
        verbose_name="اللون المُلعب"
    )
    
    class Meta:
        verbose_name = "إحصاءات افتتاح"
        verbose_name_plural = "إحصاءات الافتتاحات"
        unique_together = ['player', 'opening_name', 'eco_code']
    
    @property
    def win_rate(self):
        """حساب معدل الفوز لهذا الافتتاح"""
        if self.games_played == 0:
            return 0
        return round((self.wins / self.games_played) * 100, 1)
    
    def __str__(self):
        return f"{self.player.username} - {self.opening_name} ({self.eco_code})"
