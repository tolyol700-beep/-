import aiohttp
import asyncio
import feedparser
from bs4 import BeautifulSoup
from config import SOURCES
import logging

class ContentAggregator:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        
    async def fetch_rss(self, url):
        """Парсинг RSS-лент"""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                posts = []
                for entry in feed.entries[:10]:  # Берем 10 последних
                    post = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary if hasattr(entry, 'summary') else '',
                        'published': entry.published if hasattr(entry, 'published') else '',
                        'source': url
                    }
                    posts.append(post)
                    
                return posts
        except Exception as e:
            logging.error(f"Ошибка парсинга RSS {url}: {e}")
            return []
            
    async def fetch_web_content(self, url):
        """Парсинг веб-страниц (для источников без RSS)"""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Здесь нужно кастомная логика парсинга для каждого сайта
                # Это пример для drom.ru
                posts = []
                articles = soup.find_all('article', class_='b-news-item')[:5]
                
                for article in articles:
                    title_elem = article.find('h3') or article.find('h2')
                    if title_elem:
                        post = {
                            'title': title_elem.get_text().strip(),
                            'link': title_elem.find('a')['href'] if title_elem.find('a') else url,
                            'summary': article.get_text()[:200] + "...",
                            'source': url
                        }
                        posts.append(post)
                        
                return posts
        except Exception as e:
            logging.error(f"Ошибка парсинга веб-страницы {url}: {e}")
            return []
            
    async def fetch_content(self, content_type):
        """Основной метод сбора контента"""
        sources = SOURCES.get(content_type, [])
        all_posts = []
        
        for source in sources:
            if source.endswith('.rss') or source.endswith('.xml'):
                posts = await self.fetch_rss(source)
            else:
                posts = await self.fetch_web_content(source)
                
            all_posts.extend(posts)
            
        return all_posts