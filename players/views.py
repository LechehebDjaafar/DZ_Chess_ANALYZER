from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Player
from games.models import Game

@api_view(['GET'])
def player_list(request):
    """عرض قائمة اللاعبين المُسجّلين"""
    players = Player.objects.all().values(
        'username', 'current_rating', 'country', 'created_at'
    )
    return Response({
        'success': True,
        'players': list(players),
        'count': len(players)
    })

@api_view(['POST'])
def add_player(request):
    """إضافة لاعب جديد"""
    username = request.data.get('username')
    if not username:
        return Response({
            'success': False,
            'error': 'اسم المستخدم مطلوب'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        player, created = Player.objects.get_or_create(
            username=username,
            defaults={
                'full_name': request.data.get('full_name', ''),
                'country': request.data.get('country', 'DZ'),
                'current_rating': request.data.get('current_rating')
            }
        )
        
        return Response({
            'success': True,
            'message': 'تم إنشاء لاعب جديد' if created else 'اللاعب موجود مسبقاً',
            'player': {
                'id': player.id,
                'username': player.username,
                'full_name': player.full_name,
                'country': player.country,
                'current_rating': player.current_rating
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_player(request):
    """بدء تحليل مباريات اللاعب - نسخة مبسطة"""
    username = request.data.get('username')
    if not username:
        return Response({
            'success': False,
            'error': 'اسم المستخدم مطلوب'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # إستيراد المهمة فقط عند الحاجة
        from analysis.tasks import fetch_player_games
        
        # تشغيل مهمة جلب المباريات في الخلفية
        task = fetch_player_games.delay(username)
        
        return Response({
            'success': True,
            'message': f'تم بدء تحليل مباريات اللاعب {username}',
            'task_id': task.id
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def player_summary(request, username):
    """عرض ملخص اللاعب ومبارياته"""
    try:
        player = Player.objects.get(username=username)
        games = Game.objects.filter(player=player)
        
        # إحصاءات أساسية
        total_games = games.count()
        
        return Response({
            'success': True,
            'player': {
                'username': player.username,
                'full_name': player.full_name,
                'current_rating': player.current_rating,
                'country': player.country
            },
            'stats': {
                'total_games': total_games,
                'wins': 0,  # سنحسبها لاحقاً
                'win_percentage': 0  # سنحسبها لاحقاً
            },
            'recent_games': []  # سنملأها لاحقاً
        })
        
    except Player.DoesNotExist:
        return Response({
            'success': False,
            'error': 'اللاعب غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
