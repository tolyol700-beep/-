import os

# Настройки Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token_here")
CHANNEL_ID = "@autoinsaider_1"

# Проверенные источники (только те, которые точно работают)
SOURCES = {
    "insurance": [
        "https://www.banki.ru/news/insurance/rss/",
        "https://www.akm.ru/rss/insurance/",
    ],
    "laws": [
        "https://www.garant.ru/rss/auto/",
        "https://www.gibdd.ru/rss/news/",
    ],
    "humor": [
        "https://www.drom.ru/rss/",
        "https://fishki.net/tag/avto/rss/",
    ]
}

# Ключевые слова для фильтрации
KEYWORDS = {
    "insurance": ["ОСАГО", "страхование", "КАСКО", "полис", "страховая", "КБМ"],
    "laws": ["ПДД", "закон", "ГИБДД", "штраф", "правила", "изменения", "автоправо"],
    "humor": ["юмор", "прикол", "мем", "шутка", "смешно", "забавно"]
}
