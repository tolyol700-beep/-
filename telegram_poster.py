from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, CHANNEL_ID
import logging
from datetime import datetime

class TelegramPoster:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.channel_id = CHANNEL_ID
        
    def format_post(self, content, content_type):
        """Форматирование поста для Telegram"""
        emoji_map = {
            "insurance": "🛡️",
            "laws": "⚖️", 
            "humor": "😄"
        }
        
        title_map = {
            "insurance": "НОВОСТИ СТРАХОВАНИЯ",
            "laws": "ОБНОВЛЕНИЯ В ЗАКОНАХ",
            "humor": "АВТОЮМОР ПЯТНИЦЫ"
        }
        
        emoji = emoji_map.get(content_type, "📰")
        title = title_map.get(content_type, "НОВАЯ СТАТЬЯ")
        
        # Ограничение длины
        summary = content['summary'][:500] + "..." if len(content['summary']) > 500 else content['summary']
        
        message = f"""{emoji} <b>{title}</b>

📌 {content['title']}

📖 {summary}

🔗 <a href="{content['link']}">Читать полностью</a>
📊 Источник: {self.get_source_name(content['source'])}

💡 Наш бот для расчета страховки: @CarInsuranceFastBot

#{content_type} #{self.get_source_tag(content['source'])}"""
        
        return message
        
    def get_source_name(self, source_url):
        """Получение читаемого имени источника"""
        domain_map = {
            'banki.ru': 'Банки.ру',
            'gibdd.ru': 'ГИБДД',
            'garant.ru': 'Гарант',
            'consultant.ru': 'КонсультантПлюс',
            'drom.ru': 'Drom.ru',
            'akm.ru': 'АК&M',
            'raexpert.ru': 'РАЭКС',
            'insur-info.ru': 'Инсур-Инфо'
        }
        
        for domain, name in domain_map.items():
            if domain in source_url:
                return name
        return "Оригинальный источник"
        
    def get_source_tag(self, source_url):
        """Генерация тега для источника"""
        for domain in ['banki', 'gibdd', 'garant', 'consultant', 'drom']:
            if domain in source_url:
                return domain
        return 'autonews'
        
    async def post_to_channel(self, content, content_type):
        """Публикация поста в канал"""
        try:
            message = self.format_post(content, content_type)
            
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            
            logging.info(f"Успешно опубликован пост в канал: {content['title'][:50]}...")
            return True
            
        except TelegramError as e:
            logging.error(f"Ошибка Telegram при публикации: {e}")
            return False
        except Exception as e:
            logging.error(f"Общая ошибка при публикации: {e}")
            return False