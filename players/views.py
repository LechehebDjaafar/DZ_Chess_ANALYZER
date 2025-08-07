from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Player

@api_view(['GET'])
def player_list(request):
    """عرض قائمة اللاعبين المُسجّلين"""
    players = Player.objects.all().values('username', 'current_rating', 'country', 'created_at')
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
