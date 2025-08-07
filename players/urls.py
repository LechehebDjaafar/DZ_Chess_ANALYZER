from django.urls import path
from . import views

urlpatterns = [
    path('', views.player_list, name='player_list'),
    path('add/', views.add_player, name='add_player'),
    path('analyze/', views.analyze_player, name='analyze_player'),
    path('<str:username>/summary/', views.player_summary, name='player_summary'),
]
