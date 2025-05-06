import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class TextEntry:
    id: int
    user_id: int
    text: str
    language: str
    created_at: datetime

@dataclass
class Setting:
    id: int
    user_id: int
    key: str
    value: str
    created_at: datetime
    updated_at: datetime

@dataclass
class SessionLog:
    id: int
    user_id: int
    action: str
    details: str
    created_at: datetime

@dataclass
class Feedback:
    id: int
    user_id: int
    rating: int
    comment: str
    created_at: datetime

@dataclass
class AnalysisResult:
    id: int
    text_entry_id: int
    sentiment_label: str
    sentiment_score: float
    created_at: datetime

class DataRetrieval:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_text_entries(self, user_id: Optional[int] = None, limit: int = 100) -> List[TextEntry]:
        """Get text entries with optional user_id filter"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT * FROM text_entries 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM text_entries 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [TextEntry(
                id=row['id'],
                user_id=row['user_id'],
                text=row['text'],
                language=row['language'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in cursor.fetchall()]

    def get_settings(self, user_id: int) -> Dict[str, str]:
        """Get all settings for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT key, value FROM settings 
                WHERE user_id = ?
            ''', (user_id,))
            
            return {row['key']: row['value'] for row in cursor.fetchall()}

    def get_session_logs(self, user_id: int, limit: int = 100) -> List[SessionLog]:
        """Get session logs for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM session_logs 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            return [SessionLog(
                id=row['id'],
                user_id=row['user_id'],
                action=row['action'],
                details=row['details'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in cursor.fetchall()]

    def get_feedbacks(self, user_id: Optional[int] = None, limit: int = 100) -> List[Feedback]:
        """Get feedbacks with optional user_id filter"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT * FROM feedbacks 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM feedbacks 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [Feedback(
                id=row['id'],
                user_id=row['user_id'],
                rating=row['rating'],
                comment=row['comment'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in cursor.fetchall()]

    def get_analysis_results(self, text_entry_id: Optional[int] = None, limit: int = 100) -> List[AnalysisResult]:
        """Get analysis results with optional text_entry_id filter"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if text_entry_id:
                cursor.execute('''
                    SELECT * FROM analysis_results 
                    WHERE text_entry_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (text_entry_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM analysis_results 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [AnalysisResult(
                id=row['id'],
                text_entry_id=row['text_entry_id'],
                sentiment_label=row['sentiment_label'],
                sentiment_score=row['sentiment_score'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in cursor.fetchall()] 