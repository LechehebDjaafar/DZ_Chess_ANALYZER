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
    path('<str:username>/recommendations/', views.player_recommendations, name='player_recommendations'),
    
    # APIs Celery
    path('analyze-bg/', views.start_player_analysis, name='start_analysis'),
    path('task-status/<str:task_id>/', views.task_status, name='task_status'),
    path('create-mock/', views.create_mock_data, name='create_mock_data'),
    
    # APIs التحليل العادي
    path('analyze/', views.analyze_player, name='analyze_player'),
    path('fetch/', views.fetch_player_data, name='fetch_player_data'),

]
