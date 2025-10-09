import asyncio
import logging
import os
import random
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
        
        # Резервный контент на случай недоступности источников
        self.fallback_content = {
            "insurance": [
                {
                    'title': 'ОСАГО: что изменилось в 2024 году',
                    'summary': 'Рассматриваем основные изменения в правилах ОСАГО, которые вступили в силу в 2024 году. Новые тарифы, условия и рекомендации для автовладельцев.',
                    'link': 'https://www.vesti.ru/finance/article/3456789',
                    'source': 'Резервный источник'
                }
            ],
            "laws": [
                {
                    'title': 'Новые штрафы ГИБДД 2024',
                    'summary': 'Обзор новых штрафов за нарушение ПДД, которые начали действовать с 2024 года. Все изменения, которые должен знать каждый водитель.',
                    'link': 'https://www.gazeta.ru/auto/news/2024/02/15/12345.shtml',
                    'source': 'Резервный источник'
                }
            ],
            "humor": [
                {
                    'title': 'Автомобильные приколы',
                    'summary': 'Смешные ситуации на дорогах и в автосервисах. Юмор, который поймут только водители!',
                    'link': 'https://www.anekdot.ru/',
                    'source': 'Резервный источник'
                }
            ]
        }

    async def collect_and_post_insurance(self):
        await self.collect_and_post("insurance")
        
    async def collect_and_post_laws(self):
        await self.collect_and_post("laws")
        
    async def collect_and_post_humor(self):
        await self.collect_and_post("humor")

    async def collect_and_post(self, content_type):
        """Основной метод сбора и публикации контента"""
        try:
            logging.info(f"🔄 Начинаем сбор контента для {content_type}")
            
            # Сбор контента
            raw_content = await self.aggregator.fetch_content(content_type)
            
            if not raw_content:
                logging.warning("❌ Не удалось собрать контент, используем резервный")
                raw_content = self.fallback_content.get(content_type, [])
            
            if not raw_content:
                logging.error("❌ Нет контента для публикации")
                return

            # Проверка и фильтрация
            verified_content = await self.verifier.verify_content(raw_content, content_type)
            
            if not verified_content:
                logging.warning("⚠️ Не найдено проверенного контента, используем первый доступный")
                verified_content = raw_content[:1]  # Берем первый пост

            logging.info(f"✅ Для публикации доступно {len(verified_content)} материалов")
            
            if verified_content:
                # Выбор лучшего поста
                best_post = self.verifier.select_best_post(verified_content)
                
                # Проверяем, не публиковали ли уже
                if not self.db.is_posted(best_post['title'], best_post['source']):
                    # Публикация
                    success = await self.poster.post_to_channel(best_post, content_type)
                    
                    if success:
                        await self.db.save_post(best_post, content_type)
                        logging.info(f"✅ Успешно опубликован пост: {best_post['title'][:50]}...")
                    else:
                        logging.error("❌ Ошибка публикации поста")
                else:
                    logging.info("⚠️ Пост уже был опубликован ранее, пропускаем")
            else:
                logging.error("❌ Не удалось найти подходящий контент для публикации")
                
        except Exception as e:
            logging.error(f"❌ Ошибка в процессе публикации: {e}")

    def setup_schedule(self):
        """Настройка расписания"""
        # Понедельник 9:00 MSK - Страхование
        self.scheduler.add_job(
            self.collect_and_post_insurance,
            CronTrigger(day_of_week='mon', hour=6, minute=0),  # 9:00 MSK = 6:00 UTC
            id='monday_insurance'
        )
        
        # Среда 9:00 MSK - Законы
        self.scheduler.add_job(
            self.collect_and_post_laws,
            CronTrigger(day_of_week='wed', hour=6, minute=0),
            id='wednesday_laws'
        )
        
        # Пятница 9:00 MSK - Юмор
        self.scheduler.add_job(
            self.collect_and_post_humor,
            CronTrigger(day_of_week='fri', hour=6, minute=0),
            id='friday_humor'
        )

    async def run(self):
        """Запуск агента"""
        logging.info("🚀 Запуск агента АвтоИнсайдера...")
        
        # Проверяем подключение к Telegram
        try:
            test_success = await self.poster.test_connection()
            if not test_success:
                logging.error("❌ Не удалось подключиться к Telegram")
                return
        except Exception as e:
            logging.error(f"❌ Ошибка подключения к Telegram: {e}")
            return
        
        # Настройка расписания
        self.setup_schedule()
        self.scheduler.start()
        
        # Тестовая публикация при запуске
        logging.info("🧪 Тестовый запуск...")
        await self.collect_and_post("insurance")
        
        logging.info("⏰ Агент запущен. Ожидание расписания...")
        logging.info("📅 Расписание: ПН 9:00 - Страхование, СР 9:00 - Законы, ПТ 9:00 - Юмор (по МСК)")
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(3600)  # Проверка каждый час

async def main():
    # Проверяем наличие токена
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_bot_token_here":
        logging.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        logging.error("💡 Установите переменную окружения TELEGRAM_BOT_TOKEN")
        return
    
    agent = AutoInsiderAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
