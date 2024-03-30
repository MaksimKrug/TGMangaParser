import os
from typing import Dict, List, Optional, Tuple

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.consts import IS_READ
from src.model import MangaArtifacts, MangaChapter
from src.utils import create_logger

# logger
logger = create_logger()

# Connect to MongoDB
client: MongoClient = MongoClient(os.environ['MONGO_URL'])


def get_db(db_name: str):
    # create or access a database
    db = client[db_name]

    return db


def _get_chapter_id(
    collection: Collection, chapter: MangaChapter
) -> Optional[ObjectId]:
    mongo_doc = _find_chapter(collection, chapter)
    if mongo_doc is None:
        return None
    return mongo_doc['_id']


def _is_read_chapter(collection: Collection, chapter: MangaChapter) -> bool:
    """Check have we read the chapter already"""
    mongo_doc = _find_chapter(collection, chapter)
    if mongo_doc is None:
        _insert_chapter(collection, chapter)
        return False
    return mongo_doc[IS_READ]


def _insert_chapter(collection: Collection, chapter: MangaChapter):
    """Insert data into mongodb collection"""
    collection.insert_one(chapter.model_dump())


def _find_chapter(collection: Collection, chapter: MangaChapter) -> Optional[Dict]:
    """Check do we have the document in collection"""
    res = collection.find_one({'title': chapter.title})
    return res


def _find_chapter_by_id(
    db: Database, object_id: ObjectId
) -> Optional[Tuple[Collection, Dict]]:
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        mongo_doc = collection.find_one({'_id': ObjectId(object_id)})
        if mongo_doc is not None:
            return collection, mongo_doc
    return None


def mark_chapter_as_read(db: Database, object_id: ObjectId) -> Optional[Dict]:
    """mark chapter as read"""
    mongo_doc = _find_chapter_by_id(db, object_id)
    if mongo_doc is None:
        logger.info("Can't find chapter: %i", object_id)
    else:
        collection, chapter = mongo_doc
        if IS_READ in chapter:
            filter_query = {'_id': chapter['_id']}
            update_query = {'$set': {IS_READ: True}}
            collection.update_one(filter_query, update_query)
        else:
            ValueError('Check is_read field existence')

    return chapter


def get_new_chapters(db: Database, manga: MangaArtifacts) -> List[MangaChapter]:
    """
    Check parsed manga chapters and get all chapters we already read
    """
    # get collection
    collection = db[manga.title]
    # find not read chapters
    not_read_chapters = []
    for chapter in manga.chapters:
        read_chapter = _is_read_chapter(collection, chapter)
        if not read_chapter:
            chapter.id = _get_chapter_id(collection, chapter)
            not_read_chapters.append(chapter)

    return not_read_chapters
