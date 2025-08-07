from django.core.management.base import BaseCommand
from players.models import Player, PlayerStats, OpeningStat
from games.models import Game
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'إنشاء بيانات اختبار للموقع'

    def handle(self, *args, **options):
        self.stdout.write('بدء إنشاء بيانات الاختبار...')
        
        # إنشاء لاعبين
        players_data = [
            {'username': 'ahmed_dz', 'full_name': 'أحمد الجزائري', 'rating': 1650},
            {'username': 'fatima_alger', 'full_name': 'فاطمة الجزائرية', 'rating': 1520},
            {'username': 'youcef_chess', 'full_name': 'يوسف الشطرنجي', 'rating': 1780},
        ]
        
        players = []
        for data in players_data:
            player, created = Player.objects.get_or_create(
                username=data['username'],
                defaults={
                    'full_name': data['full_name'],
                    'current_rating': data['rating'],
                    'country': 'DZ'
                }
            )
            players.append(player)
            if created:
                self.stdout.write(f'تم إنشاء اللاعب: {player.username}')
        
        # إنشاء إحصاءات للاعبين
        openings = [
            {'name': 'الافتتاح الإيطالي', 'eco': 'C50'},
            {'name': 'دفاع الصقلي', 'eco': 'B20'},
            {'name': 'افتتاح الملكة', 'eco': 'D00'},
            {'name': 'الافتتاح الإسباني', 'eco': 'C60'},
        ]
        
        for player in players:
            # إحصاءات اللاعب العامة
            stats, created = PlayerStats.objects.get_or_create(
                player=player,
                defaults={
                    'total_games': random.randint(50, 200),
                    'wins': random.randint(20, 80),
                    'losses': random.randint(15, 60),
                    'draws': random.randint(5, 30),
                    'favorite_opening': random.choice(openings)['name'],
                    'average_game_length': random.randint(35, 65)
                }
            )
            
            # إحصاءات الافتتاحات
            for opening in openings:
                games_played = random.randint(5, 25)
                wins = random.randint(0, games_played)
                remaining = games_played - wins
                losses = random.randint(0, remaining)
                draws = remaining - losses
                
                OpeningStat.objects.get_or_create(
                    player=player,
                    opening_name=opening['name'],
                    eco_code=opening['eco'],
                    defaults={
                        'games_played': games_played,
                        'wins': wins,
                        'losses': losses,
                        'draws': draws,
                        'color_played': random.choice(['white', 'black', 'both'])
                    }
                )
        
        self.stdout.write(
            self.style.SUCCESS('تم إنشاء بيانات الاختبار بنجاح!')
        )
