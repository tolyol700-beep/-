import asyncio
from datetime import datetime, time
from config import SCHEDULE
import logging

class Scheduler:
    def __init__(self):
        self.tasks = []
        
    async def setup_schedule(self, callback_function):
        """Настройка расписания публикаций"""
        schedule_map = {
            "monday": "insurance",
            "wednesday": "laws", 
            "friday": "humor"
        }
        
        for day, content_type in schedule_map.items():
            task = asyncio.create_task(
                self.daily_check(callback_function, content_type, SCHEDULE[day])
            )
            self.tasks.append(task)
            
    async def daily_check(self, callback, content_type, post_time):
        """Ежедневная проверка времени публикации"""
        while True:
            now = datetime.now()
            
            # Проверяем день недели и время
            if (now.strftime("%A").lower() == list(SCHEDULE.keys())[list(SCHEDULE.values()).index(post_time)] and
                now.time().hour == post_time.hour and
                now.time().minute == post_time.minute):
                
                try:
                    await callback(content_type)
                    logging.info(f"Выполнена публикация для {content_type}")
                except Exception as e:
                    logging.error(f"Ошибка при выполнении публикации: {e}")
                
                # Ждем 61 минуту чтобы не запустить дважды в одну минуту
                await asyncio.sleep(61)
            else:
                # Проверяем каждую минуту
                await asyncio.sleep(60)