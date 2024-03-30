from datetime import datetime
from enum import Enum
from typing import List, Optional

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pydantic import BaseModel


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise InvalidId('Invalid ObjectId')
        return v


class MangaChapter(BaseModel):
    id: Optional[ObjectIdStr] = None
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
