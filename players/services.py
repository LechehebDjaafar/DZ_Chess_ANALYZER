# backend/players/services.py
import requests
from typing import Dict, Optional

class ChessComAPI:
    """كلاس مبسط للتعامل مع Chess.com API"""
    
    BASE_URL = "https://api.chess.com/pub"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DZ Chess Analyzer/1.0'
        })
    
    def get_player_info(self, username: str) -> Optional[Dict]:
        """جلب معلومات اللاعب الأساسية"""
        try:
            response = self.session.get(f"{self.BASE_URL}/player/{username}")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            print(f"خطأ في جلب معلومات اللاعب {username}: {e}")
            return None
