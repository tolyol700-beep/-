import aiohttp
import asyncio
from bs4 import BeautifulSoup
from config import SOURCES
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

class ContentAggregator:
    async def fetch_rss(self, url):
        """Парсинг RSS-лент без feedparser"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        posts = []
                        try:
                            # Парсим XML напрямую
                            root = ET.fromstring(content)
                            
                            # Ищем items (RSS 2.0) или entries (Atom)
                            items = root.findall('.//item') or root.findall('.//entry')
                            
                            for item in items[:5]:  # Берем 5 последних
                                title_elem = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
                                link_elem = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
                                description_elem = item.find('description') or item.find('{http://www.w3.org/2005/Atom}summary')
                                pub_date_elem = item.find('pubDate') or item.find('{http://www.w3.org/2005/Atom}published')
                                
                                if title_elem is not None:
                                    post = {
                                        'title': title_elem.text or '',
                                        'link': link_elem.text if link_elem is not None else (link_elem.get('href') if link_elem is not None else url),
                                        'summary': description_elem.text[:300] + "..." if description_elem is not None and description_elem.text else title_elem.text or '',
                                        'published': pub_date_elem.text if pub_date_elem is not None else '',
                                        'source': url
                                    }
                                    posts.append(post)
                        except ET.ParseError:
                            # Если XML не парсится, используем BeautifulSoup
                            soup = BeautifulSoup(content, 'xml')
                            items = soup.find_all('item')[:5]
                            
                            for item in items:
                                title = item.find('title')
                                link = item.find('link')
                                description = item.find('description')
                                pub_date = item.find('pubDate')
                                
                                if title:
                                    post = {
                                        'title': title.get_text(),
                                        'link': link.get_text() if link else url,
                                        'summary': description.get_text()[:300] + "..." if description else title.get_text(),
                                        'published': pub_date.get_text() if pub_date else '',
                                        'source': url
                                    }
                                    posts.append(post)
                        
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
                        
                        # Парсим заголовок и мета-описание
                        posts = []
                        title = soup.find('title')
                        meta_description = soup.find('meta', attrs={'name': 'description'})
                        
                        if title:
                            description = ""
                            if meta_description:
                                description = meta_description.get('content', '')[:200]
                            
                            # Ищем основной контент
                            article = soup.find('article') or soup.find('div', class_=lambda x: x and ('content' in x or 'article' in x))
                            if article:
                                description = article.get_text()[:200].strip()
                            
                            post = {
                                'title': title.get_text().strip(),
                                'link': url,
                                'summary': description or "Читайте полную статью по ссылке",
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
        
        tasks = []
        for source in sources:
            if source.endswith('.rss') or source.endswith('.xml'):
                task = self.fetch_rss(source)
            else:
                task = self.fetch_web_content(source)
            tasks.append(task)
        
        # Запускаем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Ошибка при сборе контента: {result}")
                continue
            all_posts.extend(result)
                
        logging.info(f"📥 Для {content_type} собрано {len(all_posts)} постов")
        return all_posts
