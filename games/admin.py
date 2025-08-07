from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['player', 'opponent_name', 'result', 'date_played', 'player_color']
    list_filter = ['result', 'player_color', 'date_played']
    search_fields = ['player__username', 'opponent_name', 'opening_name']
    readonly_fields = ['player_won', 'is_draw', 'created_at']
    date_hierarchy = 'date_played'
