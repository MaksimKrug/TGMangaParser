from datetime import datetime
from enum import Enum
from typing import List, Optional

from bson.objectid import ObjectId
from pydantic import BaseModel


class MangaChapter(BaseModel):
    id: Optional[ObjectId] = None
    manga_title: str
    title: str
    url: str
    release_date: datetime
    is_read: bool = False


class MangaArtifacts(BaseModel):
    title: str
    chapters: List[MangaChapter]


class SupportedWebsites(str, Enum):
    MANGALIB = 'mangalib.me'
    MANGAPLUS = 'mangaplus.shueisha.co.jp'


class SupportedWebsitesUrls(str, Enum):
    MANGALIB = 'https://mangalib.me'
    MANGAPLUS = 'https://mangaplus.shueisha.co.jp/'
