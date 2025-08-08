from celery import shared_task
from celery.utils.log import get_task_logger
from players.models import Player, PlayerStats, OpeningStat
from games.models import Game
from datetime import datetime
import time
import random

logger = get_task_logger(__name__)

@shared_task(bind=True)
def analyze_player_background(self, username):
    """مهمة تحليل اللاعب في الخلفية"""
    try:
        logger.info(f"بدء تحليل اللاعب: {username}")
        
        # محاكاة معالجة طويلة
        total_steps = 5
        
        # الخطوة 1: البحث عن اللاعب
        self.update_state(
            state='PROGRESS',
            meta={'current': 1, 'total': total_steps, 'status': 'البحث عن اللاعب...'}
        )
        
        try:
            player = Player.objects.get(username=username)
        except Player.DoesNotExist:
            raise Exception(f'اللاعب {username} غير موجود في النظام')
        
        time.sleep(2)  # محاكاة معالجة
        
        # الخطوة 2: تحليل المباريات
        self.update_state(
            state='PROGRESS',
            meta={'current': 2, 'total': total_steps, 'status': 'تحليل المباريات...'}
        )
        
        games = Game.objects.filter(player=player)
        games_count = games.count()
        time.sleep(2)
        
        # الخطوة 3: حساب الإحصاءات
        self.update_state(
            state='PROGRESS',
            meta={'current': 3, 'total': total_steps, 'status': 'حساب الإحصاءات...'}
        )
        
        wins = sum(1 for game in games if game.player_won)
        draws = sum(1 for game in games if game.is_draw)
        losses = games_count - wins - draws
        
        time.sleep(2)
        
        # الخطوة 4: تحديث قاعدة البيانات
        self.update_state(
            state='PROGRESS',
            meta={'current': 4, 'total': total_steps, 'status': 'تحديث قاعدة البيانات...'}
        )
        
        stats, created = PlayerStats.objects.get_or_create(
            player=player,
            defaults={
                'total_games': games_count,
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'last_analysis': datetime.now()
            }
        )
        
        if not created:
            stats.total_games = games_count
            stats.wins = wins
            stats.losses = losses
            stats.draws = draws
            stats.last_analysis = datetime.now()
            stats.save()
        
        time.sleep(1)
        
        # الخطوة 5: اكتمال التحليل
        self.update_state(
            state='PROGRESS',
            meta={'current': 5, 'total': total_steps, 'status': 'اكتمال التحليل...'}
        )
        
        logger.info(f"اكتمل تحليل اللاعب: {username}")
        
        return {
            'status': 'مكتمل',
            'message': f'تم تحليل اللاعب {username} بنجاح',
            'stats': {
                'total_games': games_count,
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'win_percentage': round((wins / games_count) * 100, 1) if games_count > 0 else 0
            }
        }
        
    except Exception as exc:
        logger.error(f"خطأ في تحليل اللاعب {username}: {exc}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc)}
        )
        raise exc

@shared_task
def simulate_chess_analysis(player_id, game_count=50):
    """مهمة محاكاة تحليل مباريات شطرنج معقدة"""
    try:
        player = Player.objects.get(id=player_id)
        
        # محاكاة إنشاء مباريات وهمية للاختبار
        openings = [
            ('الافتتاح الإيطالي', 'C50'),
            ('دفاع الصقلي', 'B20'),
            ('افتتاح الملكة', 'D00'),
            ('الافتتاح الإسباني', 'C60'),
            ('دفاع الفرنسي', 'C00')
        ]
        
        results = ['1-0', '0-1', '1/2-1/2']
        colors = ['white', 'black']
        
        for i in range(game_count):
            opening = random.choice(openings)
            
            game = Game.objects.create(
                player=player,
                opponent_name=f"Opponent_{i+1}",
                opponent_rating=random.randint(1200, 2000),
                pgn_content=f"[Mock PGN for game {i+1}]",
                result=random.choice(results),
                date_played=datetime.now().date(),
                time_control="10+0",
                player_color=random.choice(colors),
                opening_name=opening[0],
                opening_eco=opening[1],
                moves_count=random.randint(20, 80)
            )
            
            # تحديث إحصاءات الافتتاح
            opening_stat, created = OpeningStat.objects.get_or_create(
                player=player,
                opening_name=opening[0],
                eco_code=opening[1],
                defaults={
                    'games_played': 0,
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'color_played': 'both'
                }
            )
            
            opening_stat.games_played += 1
            
            if game.player_won:
                opening_stat.wins += 1
            elif game.is_draw:
                opening_stat.draws += 1
            else:
                opening_stat.losses += 1
                
            opening_stat.save()
        
        return f"تم إنشاء {game_count} مباراة وهمية للاعب {player.username}"
        
    except Exception as exc:
        raise exc

@shared_task
def cleanup_old_analysis():
    """مهمة تنظيف التحليلات القديمة"""
    from datetime import timedelta
    
    old_date = datetime.now() - timedelta(days=30)
    
    # حذف الإحصاءات القديمة (هذا مثال - كن حذراً مع حذف البيانات)
    old_stats = PlayerStats.objects.filter(last_analysis__lt=old_date)
    count = old_stats.count()
    
    logger.info(f"تم العثور على {count} إحصاءات قديمة")
    
    return f"تم تنظيف {count} سجل قديم"
