import asyncio
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from content_aggregator import ContentAggregator
from content_verifier import ContentVerifier
from telegram_poster import TelegramPoster
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
        self.scheduler = AsyncIOScheduler()
        
    async def collect_and_post_insurance(self):
        """Сбор и публикация контента по страхованию"""
        await self.collect_and_post("insurance")
        
    async def collect_and_post_laws(self):
        """Сбор и публикация контента по законам"""
        await self.collect_and_post("laws")
        
    async def collect_and_post_humor(self):
        """Сбор и публикация контента по юмору"""
        await self.collect_and_post("humor")

    async def collect_and_post(self, content_type):
        """Основной метод сбора и публикации контента"""
        try:
            logging.info(f"🔄 Начинаем сбор контента для {content_type}")
            
            # Сбор контента
            raw_content = await self.aggregator.fetch_content(content_type)
            
            if not raw_content:
                logging.warning("❌ Не удалось собрать контент")
                return

            # Проверка и фильтрация
            verified_content = await self.verifier.verify_content(raw_content, content_type)
            logging.info(f"✅ Проверено {len(verified_content)} материалов")
            
            if verified_content:
                # Выбор лучшего поста
                best_post = self.verifier.select_best_post(verified_content)
                
                # Публикация
                success = await self.poster.post_to_channel(best_post, content_type)
                
                if success:
                    await self.db.save_post(best_post, content_type)
                    logging.info(f"✅ Успешно опубликован пост: {best_post['title'][:50]}...")
                else:
                    logging.error("❌ Ошибка публикации поста")
            else:
                logging.warning("⚠️ Не найдено подходящего контента для публикации")
                
        except Exception as e:
            logging.error(f"❌ Ошибка в процессе публикации: {e}")

    def setup_schedule(self):
        """Настройка расписания"""
        # Понедельник 9:00 - Страхование (по Москве)
        self.scheduler.add_job(
            self.collect_and_post_insurance,
            CronTrigger(day_of_week='mon', hour=6, minute=0),  # 9:00 MSK = 6:00 UTC
            id='monday_insurance'
        )
        
        # Среда 9:00 - Законы
        self.scheduler.add_job(
            self.collect_and_post_laws,
            CronTrigger(day_of_week='wed', hour=6, minute=0),
            id='wednesday_laws'
        )
        
        # Пятница 9:00 - Юмор
        self.scheduler.add_job(
            self.collect_and_post_humor,
            CronTrigger(day_of_week='fri', hour=6, minute=0),
            id='friday_humor'
        )

    async def run(self):
        """Запуск агента"""
        logging.info("🚀 Запуск агента АвтоИнсайдера...")
        
        # Настройка расписания
        self.setup_schedule()
        self.scheduler.start()
        
        # Тестовая публикация при запуске
        logging.info("🧪 Тестовый запуск...")
        await self.collect_and_post_insurance()
        
        logging.info("⏰ Агент запущен. Ожидание расписания...")
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(3600)  # Проверка каждый час

async def main():
    # Проверяем наличие токена
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_bot_token_here":
        logging.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    agent = AutoInsiderAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
