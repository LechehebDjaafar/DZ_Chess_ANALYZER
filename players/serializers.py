from rest_framework import serializers
from .models import Player, PlayerStats, OpeningStat
from games.models import Game

class PlayerSerializer(serializers.ModelSerializer):
    """مسلسل بيانات اللاعب"""
    win_percentage = serializers.SerializerMethodField()
    total_games = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = ['id', 'username', 'full_name', 'country', 'current_rating', 
                 'avatar_url', 'created_at', 'win_percentage', 'total_games']
    
    def get_win_percentage(self, obj):
        """حساب نسبة الفوز"""
        try:
            stats = obj.playerstats
            return stats.win_percentage
        except:
            return 0
    
    def get_total_games(self, obj):
        """حساب إجمالي المباريات"""
        try:
            stats = obj.playerstats
            return stats.total_games
        except:
            return 0

class PlayerStatsSerializer(serializers.ModelSerializer):
    """مسلسل إحصاءات اللاعب"""
    player_username = serializers.CharField(source='player.username', read_only=True)
    win_percentage = serializers.ReadOnlyField()
    loss_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = PlayerStats
        fields = ['player_username', 'total_games', 'wins', 'losses', 'draws',
                 'win_percentage', 'loss_percentage', 'favorite_opening',
                 'weakest_defense', 'average_game_length', 'last_analysis']

class OpeningStatSerializer(serializers.ModelSerializer):
    """مسلسل إحصاءات الافتتاحات"""
    player_username = serializers.CharField(source='player.username', read_only=True)
    win_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = OpeningStat
        fields = ['player_username', 'opening_name', 'eco_code', 'games_played',
                 'wins', 'losses', 'draws', 'win_rate', 'color_played']

class GameSerializer(serializers.ModelSerializer):
    """مسلسل بيانات المباراة"""
    player_username = serializers.CharField(source='player.username', read_only=True)
    player_won = serializers.ReadOnlyField()
    is_draw = serializers.ReadOnlyField()
    
    class Meta:
        model = Game
        fields = ['id', 'player_username', 'opponent_name', 'opponent_rating',
                 'result', 'date_played', 'time_control', 'player_color',
                 'opening_name', 'opening_eco', 'moves_count', 'game_url',
                 'player_won', 'is_draw']
