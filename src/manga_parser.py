import re
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import List
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from src.consts import MANGAPLUS_LAST_CHAPTERS, manga_urls
from src.model import (
    MangaArtifacts,
    MangaChapter,
    SupportedWebsites,
    SupportedWebsitesUrls,
)
from src.utils import create_logger

# logger
logger = create_logger


def parse_date(date_string: str, date_format: str) -> datetime:
    """Parse date"""
    datetime.strptime(date_string, date_format)
    return datetime.strptime(date_string, date_format)


def get_chrome_drive() -> WebDriver:
    """Return selenium web driver for Chrome"""
    driver = webdriver.Chrome()
    return driver


def get_html_content(url: str) -> str:
    """Parse html content of the page using selenium"""
    driver = get_chrome_drive()
    driver.get(url)
    driver.implicitly_wait(3)
    html_content = driver.page_source
    driver.quit()

    return html_content


def parse_page(manga_title: str, url: str, html_content: WebElement) -> MangaArtifacts:
    """Parse html_content of the web page"""
    # get website_name: mangalib or mangaplus
    parsed_url = urlparse(url)
    website_name = parsed_url.netloc
    if website_name == SupportedWebsites.MANGALIB:
        chapters = parse_mangalib_page(manga_title, html_content)
    elif website_name == SupportedWebsites.MANGAPLUS:
        chapters = parse_mangaplus_page(manga_title, html_content)
    else:
        raise ValueError(f'{website_name} website is not supported.')

    return MangaArtifacts(title=manga_title, chapters=chapters)


def parse_mangalib_page(
    manga_title: str, html_content: WebElement
) -> List[MangaChapter]:
    """Parse mangalib html content"""
    # convert to beautiful soup format
    soup = BeautifulSoup(html_content, 'html.parser')
    # get all chapters
    all_chapters = soup.find_all('div', class_='vue-recycle-scroller__item-view')
    # parse all chapters
    chapters_data = []
    for chapter in all_chapters:
        chapter_title = chapter.find(
            'div', class_='media-chapter__name text-truncate'
        ).text.strip()
        chapter_url = (
            SupportedWebsitesUrls.MANGALIB
            + chapter.find('a', class_='link-default')['href']
        )
        release_date = chapter.find('div', class_='media-chapter__date').text.strip()
        release_date = parse_date(release_date, '%d.%m.%Y')
        chapters_data.append(
            MangaChapter(
                manga_title=manga_title,
                title=chapter_title,
                url=chapter_url,
                release_date=release_date,
            )
        )
    return chapters_data


def parse_mangaplus_page(
    manga_title: str, html_content: WebElement
) -> List[MangaChapter]:
    """Parse mangaplus html content"""
    # convert to beautiful soup format
    soup = BeautifulSoup(html_content, 'html.parser')
    # get all chapters
    all_chapters = soup.find(class_='TitleDetail-module_main_19fsJ')
    all_chapters = all_chapters.findAll(
        class_='ChapterListItem-module_chapterListItem_ykICp'
    )
    all_chapters = all_chapters[-MANGAPLUS_LAST_CHAPTERS:]
    # parse all chapters (only last three)
    chapters_data = []
    for chapter in all_chapters:
        chapter_title = chapter.find(class_='ChapterListItem-module_title_3Id89').text
        release_date = chapter.find(class_='ChapterListItem-module_date_xe1XF').text
        release_date = parse_date(release_date, '%b %d, %Y')
        chapter_url = re.findall(
            r'\/chapter\/(\d{7})\/', chapter.find('img')['data-src']
        )[0]
        chapter_url = SupportedWebsitesUrls.MANGAPLUS + '/viewer/' + chapter_url
        chapters_data.append(
            MangaChapter(
                manga_title=manga_title,
                title=chapter_title,
                url=chapter_url,
                release_date=release_date,
            )
        )
    return chapters_data


def parse_urls():
    """Parse all urls"""
    # collect html_code for each page
    with ThreadPoolExecutor() as executor:
        # Submit scraping tasks to the executor
        futures = [
            (manga_title, url, executor.submit(get_html_content, url))
            for manga_title, url in manga_urls.items()
        ]

    # process html_code
    for manga_title, url, future_res in futures:
        res = parse_page(manga_title, url, future_res.result())
        yield res
