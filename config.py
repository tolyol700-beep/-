import os
from datetime import time

# Настройки Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@autoinsaider_1"

# Расписание публикаций
SCHEDULE = {
    "monday": time(9, 0),    # ОСАГО и страхование
    "wednesday": time(9, 0), # Законы и ПДД
    "friday": time(9, 0)     # Юмор и лайфхаки
}

# Проверенные источники
SOURCES = {
    "insurance": [
        "https://www.banki.ru/news/insurance/rss/",
        "https://www.insur-info.ru/rss/",
        "https://www.akm.ru/rss/insurance/",
        "https://www.raexpert.ru/rss/insurance/"
    ],
    "laws": [
        "https://www.garant.ru/rss/auto/",
        "https://www.gibdd.ru/rss/news/",
        "https://www.consultant.ru/law/podborki/avtomobilnoe_pravo/",
        "https://legalacts.ru/rss/avto/"
    ],
    "humor": [
        "https://www.drom.ru/rss/",
        "https://www.auto.mail.ru/rss/humor/",
        "https://fishki.net/tag/avto/rss/",
        "https://pikabu.ru/rss/tag_автомобили.xml"
    ]
}

# Ключевые слова для фильтрации
KEYWORDS = {
    "insurance": ["ОСАГО", "страхование", "КАСКО", "полис", "страховая", "КБМ"],
    "laws": ["ПДД", "закон", "ГИБДД", "штраф", "правила", "изменения", "автоправо"],
    "humor": ["юмор", "прикол", "мем", "шутка", "смешно", "забавно"]
}