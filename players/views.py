from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Avg
from .models import Player, PlayerStats, OpeningStat
from games.models import Game
from .serializers import (PlayerSerializer, PlayerStatsSerializer, 
                         OpeningStatSerializer, GameSerializer)
from utils.data_helpers import update_player_stats, get_opening_recommendations

@api_view(['GET'])
def player_list(request):
    """عرض قائمة اللاعبين مع الإحصاءات الأساسية"""
    players = Player.objects.all()
    serializer = PlayerSerializer(players, many=True)
    return Response({
        'success': True,
        'players': serializer.data,
        'count': players.count()
    })

@api_view(['POST'])
def add_player(request):
    """إضافة لاعب جديد مع إنشاء إحصاءات فارغة"""
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
        
        # إنشاء إحصاءات فارغة للاعب الجديد
        if created:
            PlayerStats.objects.create(player=player)
        
        serializer = PlayerSerializer(player)
        return Response({
            'success': True,
            'message': 'تم إنشاء لاعب جديد' if created else 'اللاعب موجود مسبقاً',
            'player': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def player_detail(request, username):
    """عرض تفاصيل اللاعب الكاملة"""
    try:
        player = Player.objects.get(username=username)
        
        # بيانات اللاعب الأساسية
        player_data = PlayerSerializer(player).data
        
        # إحصاءات اللاعب
        try:
            stats = player.playerstats
            stats_data = PlayerStatsSerializer(stats).data
        except PlayerStats.DoesNotExist:
            stats_data = None
        
        # إحصاءات الافتتاحات
        openings = OpeningStat.objects.filter(player=player)
        openings_data = OpeningStatSerializer(openings, many=True).data
        
        # آخر المباريات
        recent_games = Game.objects.filter(player=player).order_by('-date_played')[:10]
        games_data = GameSerializer(recent_games, many=True).data
        
        return Response({
            'success': True,
            'player': player_data,
            'stats': stats_data,
            'openings': openings_data,
            'recent_games': games_data
        })
        
    except Player.DoesNotExist:
        return Response({
            'success': False,
            'error': 'اللاعب غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def player_openings_analysis(request, username):
    """تحليل تفصيلي لافتتاحات اللاعب"""
    try:
        player = Player.objects.get(username=username)
        openings = OpeningStat.objects.filter(player=player).order_by('-win_rate')
        
        if not openings.exists():
            return Response({
                'success': False,
                'message': 'لا توجد بيانات افتتاحات لهذا اللاعب'
            })
        
        # تصنيف الافتتاحات
        best_openings = openings.filter(win_rate__gte=60)[:5]
        worst_openings = openings.filter(win_rate__lt=40)[:5]
        most_played = openings.order_by('-games_played')[:5]
        
        return Response({
            'success': True,
            'player_username': username,
            'analysis': {
                'best_openings': OpeningStatSerializer(best_openings, many=True).data,
                'worst_openings': OpeningStatSerializer(worst_openings, many=True).data,
                'most_played': OpeningStatSerializer(most_played, many=True).data,
                'total_openings': openings.count()
            }
        })
        
    except Player.DoesNotExist:
        return Response({
            'success': False,
            'error': 'اللاعب غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def player_performance_stats(request, username):
    """إحصاءات الأداء المتقدمة"""
    try:
        player = Player.objects.get(username=username)
        games = Game.objects.filter(player=player)
        
        # إحصاءات عامة
        total_games = games.count()
        if total_games == 0:
            return Response({
                'success': False,
                'error': 'لا توجد مباريات لهذا اللاعب'
            })
        
        # إحصاءات حسب اللون
        white_games = games.filter(player_color='white')
        black_games = games.filter(player_color='black')
        
        white_wins = white_games.filter(result='1-0').count()
        black_wins = black_games.filter(result='0-1').count()
        
        return Response({
            'success': True,
            'player_username': username,
            'performance': {
                'total_games': total_games,
                'color_stats': {
                    'as_white': {
                        'games': white_games.count(),
                        'wins': white_wins,
                        'win_rate': round((white_wins / white_games.count()) * 100, 1) if white_games.count() > 0 else 0
                    },
                    'as_black': {
                        'games': black_games.count(),
                        'wins': black_wins,
                        'win_rate': round((black_wins / black_games.count()) * 100, 1) if black_games.count() > 0 else 0
                    }
                }
            }
        })
        
    except Player.DoesNotExist:
        return Response({
            'success': False,
            'error': 'اللاعب غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def leaderboard(request):
    """لوحة الصدارة للاعبين"""
    # ترتيب حسب التصنيف
    by_rating = Player.objects.filter(current_rating__isnull=False).order_by('-current_rating')[:10]
    
    # ترتيب حسب نسبة الفوز
    players_with_stats = PlayerStats.objects.filter(total_games__gte=10).order_by('-wins')[:10]
    
    return Response({
        'success': True,
        'leaderboards': {
            'by_rating': PlayerSerializer(by_rating, many=True).data,
            'by_wins': [
                {
                    'username': stat.player.username,
                    'wins': stat.wins,
                    'win_percentage': stat.win_percentage,
                    'total_games': stat.total_games
                } for stat in players_with_stats
            ]
        }
    })

@api_view(['GET'])
def player_recommendations(request, username):
    """توصيات تحسين الأداء للاعب"""
    try:
        player = Player.objects.get(username=username)
        
        # تحديث الإحصاءات أولاً
        update_player_stats(player)
        
        # الحصول على التوصيات
        recommendations = get_opening_recommendations(player)
        
        return Response({
            'success': True,
            'player_username': username,
            'recommendations': recommendations
        })
        
    except Player.DoesNotExist:
        return Response({
            'success': False,
            'error': 'اللاعب غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def analyze_player(request):
    """تحليل مباريات اللاعب - نسخة مبسطة"""
    username = request.data.get('username')
    if not username:
        return Response({
            'success': False,
            'error': 'اسم المستخدم مطلوب'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        player = Player.objects.get(username=username)
        
        # تحديث إحصاءات اللاعب
        stats = update_player_stats(player)
        
        return Response({
            'success': True,
            'message': f'تم تحليل مباريات اللاعب {username} بنجاح',
            'player': PlayerSerializer(player).data,
            'stats_updated': stats is not None
        })
        
    except Player.DoesNotExist:
        return Response({
            'success': False,
            'error': 'اللاعب غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from .chess_api import ChessComAPI
from analysis.data_processor import GameDataProcessor
from datetime import datetime

@api_view(['POST'])
def fetch_player_data(request):
    """جلب وتحليل بيانات اللاعب من Chess.com"""
    username = request.data.get('username')
    months_count = request.data.get('months', 3)  # عدد الأشهر الافتراضي
    
    if not username:
        return Response({
            'success': False,
            'error': 'اسم المستخدم مطلوب'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # تهيئة الخدمات
        chess_api = ChessComAPI()
        data_processor = GameDataProcessor()
        
        # التحقق من وجود اللاعب على Chess.com
        player_info = chess_api.get_player_info(username)
        if not player_info:
            return Response({
                'success': False,
                'error': f'لم يتم العثور على اللاعب {username} في Chess.com'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # إنشاء أو تحديث سجل اللاعب
        player, created = Player.objects.get_or_create(
            username=username,
            defaults={
                'full_name': player_info.get('name', ''),
                'country': player_info.get('country', '').split('/')[-1] if player_info.get('country') else 'DZ',
                'avatar_url': player_info.get('avatar', '')
            }
        )
        
        # تحديث التصنيف الحالي
        stats_data = chess_api.get_player_stats(username)
        if stats_data and 'chess_rapid' in stats_data:
            rating_info = stats_data['chess_rapid'].get('last', {})
            player.current_rating = rating_info.get('rating')
            player.save()
        
        # جلب المباريات
        logger.info(f"بدء جلب مباريات اللاعب {username} لآخر {months_count} أشهر")
        games_data = chess_api.get_recent_games(username, months_count)
        
        if not games_data:
            return Response({
                'success': False,
                'error': 'لا توجد مباريات متاحة للاعب'
            })
        
        # معالجة المباريات
        processing_result = data_processor.process_games_batch(player, games_data)
        
        return Response({
            'success': True,
            'message': f'تم تحليل بيانات اللاعب {username} بنجاح',
            'player': PlayerSerializer(player).data,
            'processing': {
                'total_fetched': len(games_data),
                'processed': processing_result['processed'],
                'skipped': processing_result['skipped'],
                'new_openings': processing_result['new_openings']
            }
        })
        
    except Exception as e:
        logger.error(f"خطأ في جلب بيانات اللاعب {username}: {e}")
        return Response({
            'success': False,
            'error': f'خطأ في معالجة البيانات: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
