import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
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

class DataInsertion:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def insert_text_entry(self, user_id: int, text: str, language: str) -> Optional[int]:
        """Insert a new text entry and return its ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO text_entries (user_id, text, language, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, text, language, datetime.now().isoformat()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting text entry: {e}")
            return None

    def insert_setting(self, user_id: int, key: str, value: str) -> bool:
        """Insert or update a user setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if setting exists
                cursor.execute('''
                    SELECT id FROM settings 
                    WHERE user_id = ? AND key = ?
                ''', (user_id, key))
                
                if cursor.fetchone():
                    # Update existing setting
                    cursor.execute('''
                        UPDATE settings 
                        SET value = ?, updated_at = ?
                        WHERE user_id = ? AND key = ?
                    ''', (value, datetime.now().isoformat(), user_id, key))
                else:
                    # Insert new setting
                    cursor.execute('''
                        INSERT INTO settings (user_id, key, value, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, key, value, datetime.now().isoformat(), datetime.now().isoformat()))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error inserting/updating setting: {e}")
            return False

    def insert_session_log(self, user_id: int, action: str, details: str) -> bool:
        """Insert a new session log"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO session_logs (user_id, action, details, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, action, details, datetime.now().isoformat()))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error inserting session log: {e}")
            return False

    def insert_feedback(self, user_id: int, rating: int, comment: str) -> bool:
        """Insert a new feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO feedbacks (user_id, rating, comment, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, rating, comment, datetime.now().isoformat()))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error inserting feedback: {e}")
            return False

    def insert_analysis_result(self, text_entry_id: int, sentiment_label: str, sentiment_score: float) -> bool:
        """Insert a new analysis result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analysis_results (text_entry_id, sentiment_label, sentiment_score, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (text_entry_id, sentiment_label, sentiment_score, datetime.now().isoformat()))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error inserting analysis result: {e}")
            return False 