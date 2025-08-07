from django.db import models
from players.models import Player

class Game(models.Model):
    RESULT_CHOICES = [
        ('1-0', 'فوز الأبيض'),
        ('0-1', 'فوز الأسود'), 
        ('1/2-1/2', 'تعادل'),
    ]
    
    COLOR_CHOICES = [
        ('white', 'أبيض'),
        ('black', 'أسود'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="اللاعب")
    opponent_name = models.CharField(max_length=50, verbose_name="اسم الخصم")
    opponent_rating = models.IntegerField(null=True, blank=True, verbose_name="تصنيف الخصم")
    pgn_content = models.TextField(verbose_name="محتوى PGN")
    result = models.CharField(max_length=7, choices=RESULT_CHOICES, verbose_name="النتيجة")
    date_played = models.DateField(verbose_name="تاريخ اللعب")
    time_control = models.CharField(max_length=20, blank=True, verbose_name="زمن التحكم")
    player_color = models.CharField(max_length=5, choices=COLOR_CHOICES, verbose_name="لون اللاعب")
    opening_name = models.CharField(max_length=100, blank=True, verbose_name="اسم الافتتاح")
    opening_eco = models.CharField(max_length=3, blank=True, verbose_name="رمز ECO")
    moves_count = models.IntegerField(default=0, verbose_name="عدد النقلات")
    game_url = models.URLField(blank=True, verbose_name="رابط المباراة")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "مباراة"
        verbose_name_plural = "المباريات"
        unique_together = ['player', 'opponent_name', 'date_played', 'time_control']
    
    @property
    def player_won(self):
        """هل فاز اللاعب في هذه المباراة؟"""
        if self.player_color == 'white' and self.result == '1-0':
            return True
        elif self.player_color == 'black' and self.result == '0-1':
            return True
        return False
    
    @property
    def is_draw(self):
        """هل انتهت المباراة بالتعادل؟"""
        return self.result == '1/2-1/2'
    
    def __str__(self):
        return f"{self.player.username} vs {self.opponent_name} ({self.date_played})"
