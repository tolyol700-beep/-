import os

# Настройки Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token_here")
CHANNEL_ID = "@autoinsaider_1"

# Обновленные проверенные источники
SOURCES = {
    "insurance": [
        "https://www.vedomosti.ru/rss/rubric/insurance",  # Ведомости - страхование
        "https://www.kommersant.ru/RSS/section-insurance.xml",  # Коммерсант - страхование
        "https://www.rbc.ru/rbcnews.xml",  # РБК (есть страхование)
    ],
    "laws": [
        "https://www.vedomosti.ru/rss/rubric/law",  # Ведомости - право
        "https://www.kommersant.ru/RSS/section-law.xml",  # Коммерсант - право
        "https://rg.ru/rss/index.xml",  # Российская газета
    ],
    "humor": [
        "https://fishki.net/rss/tag/avto/",  # Фишки - авто
        "https://www.anekdot.ru/rss/export_j.xml",  # Анекдоты
        "https://www.drom.ru/rss/",  # Drom
    ]
}

# Ключевые слова для фильтрации
KEYWORDS = {
    "insurance": ["ОСАГО", "страхование", "КАСКО", "полис", "страховая", "КБМ", "автострахование"],
    "laws": ["ПДД", "закон", "ГИБДД", "штраф", "правила", "изменения", "автоправо", "водитель", "автомобиль"],
    "humor": ["юмор", "прикол", "мем", "шутка", "смешно", "забавно", "анекдот"]
}
