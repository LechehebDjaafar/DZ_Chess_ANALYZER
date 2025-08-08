from django.urls import path
from . import views

urlpatterns = [
    # APIs الأساسية
    path('', views.player_list, name='player_list'),
    path('add/', views.add_player, name='add_player'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # APIs تفاصيل اللاعبين
    path('<str:username>/', views.player_detail, name='player_detail'),
    path('<str:username>/openings/', views.player_openings_analysis, name='player_openings'),
    path('<str:username>/performance/', views.player_performance_stats, name='player_performance'),
    
    # APIs التحليل (سنضيفها لاحقاً)
    path('analyze/', views.analyze_player, name='analyze_player'),
    path('<str:username>/recommendations/', views.player_recommendations, name='player_recommendations'),
# إضافة هذا المسار
    path('fetch/', views.fetch_player_data, name='fetch_player_data'),

]
