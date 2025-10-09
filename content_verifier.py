import re
import aiohttp
from config import KEYWORDS
import logging

class ContentVerifier:
    def __init__(self):
        self.min_length = 100
        self.max_length = 2000
        
    async def verify_source(self, url):
        """Проверка надежности источника"""
        trusted_domains = [
            'banki.ru', 'gibdd.ru', 'garant.ru', 'consultant.ru',
            'drom.ru', 'akm.ru', 'raexpert.ru', 'insur-info.ru'
        ]
        
        return any(domain in url for domain in trusted_domains)
        
    def check_relevance(self, content, content_type):
        """Проверка релевантности по ключевым словам"""
        keywords = KEYWORDS.get(content_type, [])
        text = f"{content['title']} {content['summary']}".lower()
        
        # Считаем количество совпадений ключевых слов
        matches = sum(1 for keyword in keywords if keyword.lower() in text)
        return matches >= 2  # Минимум 2 совпадения
        
    def check_quality(self, content):
        """Проверка качества контента"""
        text = content['summary']
        
        # Проверка длины
        if len(text) < self.min_length or len(text) > self.max_length:
            return False
            
        # Проверка на спам
        spam_indicators = ['казино', 'ставки', 'xxx', 'порно', 'viagra']
        if any(indicator in text.lower() for indicator in spam_indicators):
            return False
            
        return True
        
    async def verify_content(self, raw_content, content_type):
        """Основная проверка контента"""
        verified_content = []
        
        for content in raw_content:
            try:
                # Проверка источника
                if not await self.verify_source(content['source']):
                    continue
                    
                # Проверка релевантности
                if not self.check_relevance(content, content_type):
                    continue
                    
                # Проверка качества
                if not self.check_quality(content):
                    continue
                    
                verified_content.append(content)
                
            except Exception as e:
                logging.error(f"Ошибка верификации контента: {e}")
                continue
                
        return verified_content
        
    def select_best_post(self, verified_content):
        """Выбор лучшего поста для публикации"""
        # Сортировка по дате публикации (если есть) и релевантности
        return sorted(verified_content, 
                     key=lambda x: x.get('published', ''), 
                     reverse=True)[0]