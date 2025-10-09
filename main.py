import asyncio
import logging
from datetime import datetime
from content_aggregator import ContentAggregator
from content_verifier import ContentVerifier
from telegram_poster import TelegramPoster
from scheduler import Scheduler
from database import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AutoInsiderAgent:
    def __init__(self):
        self.db = Database()
        self.aggregator = ContentAggregator()
        self.verifier = ContentVerifier()
        self.poster = TelegramPoster()
        self.scheduler = Scheduler()
        
    async def collect_and_post(self, content_type):
        """Основной метод сбора и публикации контента"""
        try:
            logging.info(f"Начинаем сбор контента для {content_type}")
            
            # Сбор контента
            raw_content = await self.aggregator.fetch_content(content_type)
            
            # Проверка и фильтрация
            verified_content = await self.verifier.verify_content(raw_content, content_type)
            
            if verified_content:
                # Выбор лучшего поста
                best_post = self.verifier.select_best_post(verified_content)
                
                # Публикация
                success = await self.poster.post_to_channel(best_post, content_type)
                
                if success:
                    await self.db.save_post(best_post)
                    logging.info(f"Успешно опубликован пост: {best_post['title'][:50]}...")
                else:
                    logging.error("Ошибка публикации поста")
            else:
                logging.warning("Не найдено подходящего контента для публикации")
                
        except Exception as e:
            logging.error(f"Ошибка в процессе публикации: {e}")

    async def run(self):
        """Запуск агента"""
        logging.info("Запуск агента АвтоИнсайдера...")
        
        # Настройка расписания
        await self.scheduler.setup_schedule(self.collect_and_post)
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(60)  # Проверка каждую минуту

if __name__ == "__main__":
    agent = AutoInsiderAgent()
    asyncio.run(agent.run())