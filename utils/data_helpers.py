from players.models import Player, PlayerStats, OpeningStat
from games.models import Game
from django.db.models import Count, Q

def update_player_stats(player):
    """تحديث إحصاءات اللاعب بناءً على مبارياته"""
    games = Game.objects.filter(player=player)
    total_games = games.count()
    
    if total_games == 0:
        return None
    
    # حساب النتائج
    wins = games.filter(
        Q(player_color='white', result='1-0') | 
        Q(player_color='black', result='0-1')
    ).count()
    
    draws = games.filter(result='1/2-1/2').count()
    losses = total_games - wins - draws
    
    # تحديث أو إنشاء الإحصاءات
    stats, created = PlayerStats.objects.get_or_create(
        player=player,
        defaults={
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'draws': draws,
        }
    )
    
    if not created:
        stats.total_games = total_games
        stats.wins = wins
        stats.losses = losses
        stats.draws = draws
        stats.save()
    
    return stats

def get_opening_recommendations(player):
    """توصيات الافتتاحات للاعب"""
    openings = OpeningStat.objects.filter(player=player)
    
    if not openings.exists():
        return {
            'recommended': [],
            'needs_improvement': [],
            'message': 'لا توجد بيانات افتتاحات لهذا اللاعب'
        }
    
    # أفضل الافتتاحات (نسبة فوز عالية + عدد مباريات معقول)
    good_openings = openings.filter(
        games_played__gte=5,
        win_rate__gte=60
    ).order_by('-win_rate')[:3]
    
    # الافتتاحات التي تحتاج تحسين
    weak_openings = openings.filter(
        games_played__gte=5,
        win_rate__lt=40
    ).order_by('win_rate')[:3]
    
    return {
        'recommended': list(good_openings.values('opening_name', 'eco_code', 'win_rate')),
        'needs_improvement': list(weak_openings.values('opening_name', 'eco_code', 'win_rate'))
    }
