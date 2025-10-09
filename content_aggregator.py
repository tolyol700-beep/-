import aiohttp
import asyncio
from bs4 import BeautifulSoup
from config import SOURCES
import logging
import re
import ssl

class ContentAggregator:
    def __init__(self):
        # Создаем кастомный SSL контекст для обхода проблем с сертификатами
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def fetch_rss(self, url):
        """Парсинг RSS-лент с улучшенной обработкой ошибок"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Пробуем разные кодировки
                        for encoding in ['utf-8', 'windows-1251', 'cp1251']:
                            try:
                                soup = BeautifulSoup(content, 'xml', from_encoding=encoding)
                                break
                            except:
                                continue
                        else:
                            soup = BeautifulSoup(content, 'xml')
                        
                        posts = []
                        
                        # Ищем items в RSS или entries в Atom
                        items = soup.find_all('item') or soup.find_all('entry')
                        
                        for item in items[:5]:  # Берем 5 последних
                            try:
                                title_elem = item.find('title')
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text().strip()
                                
                                # Получаем ссылку
                                link_elem = item.find('link')
                                if link_elem:
                                    link = link_elem.get('href') or link_elem.get_text()
                                else:
                                    guid_elem = item.find('guid')
                                    link = guid_elem.get_text() if guid_elem else url
                                
                                # Получаем описание
                                description_elem = item.find('description') or item.find('summary') or item.find('content')
                                description = ""
                                if description_elem:
                                    description = description_elem.get_text().strip()[:300]
                                
                                # Если описание пустое, используем заголовок
                                if not description:
                                    description = title
                                
                                # Получаем дату
                                pub_date_elem = item.find('pubdate') or item.find('published')
                                pub_date = pub_date_elem.get_text() if pub_date_elem else ""
                                
                                post = {
                                    'title': title,
                                    'link': link,
                                    'summary': description + "..." if len(description) > 100 else description,
                                    'published': pub_date,
                                    'source': url
                                }
                                posts.append(post)
                                
                            except Exception as e:
                                logging.warning(f"Ошибка парсинга элемента в {url}: {e}")
                                continue
                        
                        logging.info(f"✅ Успешно получено {len(posts)} постов из {url}")
                        return posts
                    else:
                        logging.warning(f"⚠️ HTTP {response.status} для {url}")
                        return []
                        
        except asyncio.TimeoutError:
            logging.error(f"⏰ Таймаут при запросе к {url}")
            return []
        except Exception as e:
            logging.error(f"❌ Ошибка парсинга RSS {url}: {str(e)}")
            return []
            
    async def fetch_web_content(self, url):
        """Парсинг веб-страниц с улучшенной обработкой"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Убираем ненужные элементы
                        for element in soup(["script", "style", "nav", "header", "footer"]):
                            element.decompose()
                        
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else "Без заголовка"
                        
                        # Ищем основной контент
                        article = (soup.find('article') or 
                                  soup.find('div', class_=re.compile('content|article|post|main')) or
                                  soup.find('main') or
                                  soup.find('body'))
                        
                        if article:
                            text = article.get_text()
                            # Очищаем текст от лишних пробелов
                            text = ' '.join(text.split())
                            summary = text[:200] + "..." if len(text) > 200 else text
                        else:
                            summary = "Читайте полную статью по ссылке"
                        
                        post = {
                            'title': title_text,
                            'link': url,
                            'summary': summary,
                            'source': url
                        }
                        return [post]
                    else:
                        logging.warning(f"⚠️ HTTP {response.status} для веб-страницы {url}")
                        return []
                        
        except asyncio.TimeoutError:
            logging.error(f"⏰ Таймаут при запросе к веб-странице {url}")
            return []
        except Exception as e:
            logging.error(f"❌ Ошибка парсинга веб-страницы {url}: {str(e)}")
            return []
            
    async def fetch_content(self, content_type):
        """Основной метод сбора контента"""
        sources = SOURCES.get(content_type, [])
        all_posts = []
        
        logging.info(f"🔍 Начинаем сбор контента типа '{content_type}' из {len(sources)} источников")
        
        for source in sources:
            try:
                if any(ext in source for ext in ['.rss', '.xml', 'rss/']):
                    posts = await self.fetch_rss(source)
                else:
                    posts = await self.fetch_web_content(source)
                    
                if posts:
                    all_posts.extend(posts)
                    logging.info(f"📰 Из {source} получено {len(posts)} постов")
                else:
                    logging.warning(f"📭 Не удалось получить посты из {source}")
                    
            except Exception as e:
                logging.error(f"🔥 Критическая ошибка при обработке источника {source}: {e}")
                continue
                
        logging.info(f"📥 Всего собрано {len(all_posts)} постов для {content_type}")
        return all_posts
