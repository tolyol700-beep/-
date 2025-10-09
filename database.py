import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path="autoinsider.db"):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS published_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, source)
                )
            ''')
            
    async def save_post(self, post_data):
        """Сохранение опубликованного поста"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR IGNORE INTO published_posts 
                    (title, content, source, content_type) 
                    VALUES (?, ?, ?, ?)
                ''', (
                    post_data['title'],
                    post_data['summary'],
                    post_data['source'],
                    'auto'  # Можно определить тип из контекста
                ))
        except Exception as e:
            print(f"Ошибка сохранения в БД: {e}")
            
    def is_posted(self, title, source):
        """Проверка, был ли пост уже опубликован"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT 1 FROM published_posts WHERE title = ? AND source = ?',
                (title, source)
            )
            return cursor.fetchone() is not None