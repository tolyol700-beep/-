import aiohttp
import asyncio
from bs4 import BeautifulSoup
from config import SOURCES
import logging
import re

class ContentAggregator:
    async def fetch_rss(self, url):
        """Парсинг RSS-лент с помощью BeautifulSoup"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        posts = []
                        
                        # Парсим RSS/Atom фиды
                        items = soup.find_all('item')[:5] or soup.find_all('entry')[:5]
                        
                        for item in items:
                            try:
                                title_elem = item.find('title')
                                link_elem = item.find('link')
                                description_elem = item.find('description') or item.find('summary')
                                pub_date_elem = item.find('pubdate') or item.find('published')
                                
                                if title_elem:
                                    title = title_elem.get_text().strip()
                                    
                                    # Получаем ссылку
                                    if link_elem:
                                        if link_elem.get('href'):
                                            link = link_elem.get('href')
                                        else:
                                            link = link_elem.get_text().strip()
                                    else:
                                        link = url
                                    
                                    # Получаем описание
                                    if description_elem:
                                        description = description_elem.get_text().strip()[:300] + "..."
                                    else:
                                        description = title
                                    
                                    # Получаем дату публикации
                                    pub_date = ""
                                    if pub_date_elem:
                                        pub_date = pub_date_elem.get_text().strip()
                                    
                                    post = {
                                        'title': title,
                                        'link': link,
                                        'summary': description,
                                        'published': pub_date,
                                        'source': url
                                    }
                                    posts.append(post)
                            except Exception as e:
                                logging.error(f"Ошибка парсинга элемента RSS: {e}")
                                continue
                        
                        return posts
                    else:
                        logging.error(f"Ошибка HTTP {response.status} для {url}")
                        return []
        except Exception as e:
            logging.error(f"Ошибка парсинга RSS {url}: {e}")
            return []
            
    async def fetch_web_content(self, url):
        """Парсинг веб-страниц"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        posts = []
                        
                        # Убираем скрипты и стили
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Получаем заголовок
                        title = soup.find('title')
                        if title:
                            title_text = title.get_text().strip()
                        else:
                            title_text = "Без заголовка"
                        
                        # Получаем основной контент
                        article = (soup.find('article') or 
                                  soup.find('div', class_=re.compile('content|article|post')) or
                                  soup.find('main') or
                                  soup)
                        
                        # Берем первые 200 символов текста
                        text_content = article.get_text().strip()
                        summary = ' '.join(text_content.split()[:30]) + "..."
                        
                        post = {
                            'title': title_text,
                            'link': url,
                            'summary': summary,
                            'source': url
                        }
                        posts.append(post)
                        return posts
                    else:
                        return []
        except Exception as e:
            logging.error(f"Ошибка парсинга веб-страницы {url}: {e}")
            return []
            
    async def fetch_content(self, content_type):
        """Основной метод сбора контента"""
        sources = SOURCES.get(content_type, [])
        all_posts = []
        
        for source in sources:
            try:
                if source.endswith('.rss') or source.endswith('.xml') or 'rss' in source:
                    posts = await self.fetch_rss(source)
                else:
                    posts = await self.fetch_web_content(source)
                    
                all_posts.extend(posts)
                logging.info(f"📰 Из {source} получено {len(posts)} постов")
                
            except Exception as e:
                logging.error(f"Ошибка при обработке источника {source}: {e}")
                continue
                
        return all_posts
