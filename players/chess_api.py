import requests
from datetime import datetime
import time
from typing import List, Dict, Optional
import chess.pgn
import io
import logging

logger = logging.getLogger(__name__)

class ChessComAPI:
    """كلاس متقدم للتعامل مع Chess.com API"""
    
    BASE_URL = "https://api.chess.com/pub"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DZ Chess Analyzer/1.0 (contact@dzchess.ai)'
        })
    
    def get_player_info(self, username: str) -> Optional[Dict]:
        """جلب معلومات اللاعب الأساسية"""
        try:
            response = self.session.get(f"{self.BASE_URL}/player/{username}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"خطأ في جلب معلومات اللاعب {username}: {e}")
            return None
    
    def get_player_stats(self, username: str) -> Optional[Dict]:
        """جلب إحصاءات اللاعب (تصنيفات مختلف الأنماط)"""
        try:
            response = self.session.get(f"{self.BASE_URL}/player/{username}/stats")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"خطأ في جلب إحصاءات اللاعب {username}: {e}")
            return None
    
    def get_game_archives(self, username: str) -> List[str]:
        """جلب قائمة أرشيف المباريات الشهرية"""
        try:
            response = self.session.get(f"{self.BASE_URL}/player/{username}/games/archives")
            response.raise_for_status()
            return response.json().get('archives', [])
        except requests.RequestException as e:
            logger.error(f"خطأ في جلب أرشيف المباريات للاعب {username}: {e}")
            return []
    
    def get_monthly_games(self, archive_url: str) -> List[Dict]:
        """جلب مباريات شهر محدد مع Rate Limiting"""
        try:
            # تأخير لتجنب Rate Limiting
            time.sleep(0.2)
            response = self.session.get(archive_url)
            response.raise_for_status()
            return response.json().get('games', [])
        except requests.RequestException as e:
            logger.error(f"خطأ في جلب المباريات من {archive_url}: {e}")
            return []
    
    def get_recent_games(self, username: str, months_count: int = 3) -> List[Dict]:
        """جلب المباريات الأخيرة للاعب"""
        archives = self.get_game_archives(username)
        if not archives:
            return []
        
        # أخذ آخر N أشهر
        recent_archives = archives[-months_count:]
        all_games = []
        
        logger.info(f"جلب مباريات {username} من {len(recent_archives)} أشهر")
        
        for archive_url in recent_archives:
            monthly_games = self.get_monthly_games(archive_url)
            all_games.extend(monthly_games)
            logger.info(f"تم جلب {len(monthly_games)} مباراة من {archive_url}")
        
        return all_games
    
    def parse_pgn_info(self, pgn_content: str, target_username: str) -> Optional[Dict]:
        """تحليل معلومات PGN واستخراج البيانات المهمة"""
        try:
            pgn_io = io.StringIO(pgn_content)
            game = chess.pgn.read_game(pgn_io)
            
            if not game:
                return None
            
            headers = game.headers
            
            # تحديد لون اللاعب المستهدف
            white_player = headers.get('White', '').lower()
            black_player = headers.get('Black', '').lower()
            target_username_lower = target_username.lower()
            
            if target_username_lower in white_player:
                player_color = 'white'
                opponent = headers.get('Black', 'مجهول')
            elif target_username_lower in black_player:
                player_color = 'black'
                opponent = headers.get('White', 'مجهول')
            else:
                return None
            
            # تحويل التاريخ
            date_str = headers.get('Date', '')
            try:
                date_obj = datetime.strptime(date_str, '%Y.%m.%d').date()
            except (ValueError, TypeError):
                date_obj = datetime.now().date()
            
            # استخراج معلومات إضافية
            time_control = headers.get('TimeControl', '')
            termination = headers.get('Termination', '')
            opening = headers.get('ECO', '')
            
            # حساب عدد النقلات
            moves_count = len(list(game.mainline_moves()))
            
            # تحديد النتيجة النهائية
            result = headers.get('Result', '1/2-1/2')
            
            return {
                'opponent': opponent,
                'result': result,
                'date': date_obj,
                'time_control': time_control,
                'player_color': player_color,
                'termination': termination,
                'opening_eco': opening,
                'moves_count': moves_count,
                'pgn_content': pgn_content
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل PGN: {e}")
            return None
    
    def extract_opening_name(self, pgn_content: str) -> tuple[str, str]:
        """استخراج اسم الافتتاح ورمز ECO"""
        try:
            pgn_io = io.StringIO(pgn_content)
            game = chess.pgn.read_game(pgn_io)
            
            if not game:
                return "غير معروف", "???"
            
            headers = game.headers
            eco_code = headers.get('ECO', '???')
            opening_name = headers.get('Opening', 'غير معروف')
            
            return opening_name, eco_code
            
        except Exception as e:
            logger.error(f"خطأ في استخراج الافتتاح: {e}")
            return "غير معروف", "???"
