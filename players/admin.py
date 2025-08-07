from django.contrib import admin
from .models import Player, PlayerStats, OpeningStat

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'country', 'current_rating', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['username', 'full_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'total_games', 'wins', 'losses', 'win_percentage']
    list_filter = ['last_analysis']
    readonly_fields = ['win_percentage', 'loss_percentage']

@admin.register(OpeningStat)
class OpeningStatAdmin(admin.ModelAdmin):
    list_display = ['player', 'opening_name', 'eco_code', 'games_played', 'win_rate']
    list_filter = ['eco_code', 'color_played']
    search_fields = ['opening_name', 'player__username']
