from src.consts import DB_NAME
from src.database import get_db, get_new_chapters, mark_chapter_as_read
from src.manga_parser import parse_urls
from src.utils import create_logger

# logger
logger = create_logger()

if __name__ == '__main__':
    parsed_manga = parse_urls()
    db = get_db(DB_NAME)
    for manga in parsed_manga:
        # get all new chapters
        new_chapters = get_new_chapters(db, manga)
        new_chapters = sorted(
            new_chapters, key=lambda chapter: chapter.release_date, reverse=True
        )
        # mark all chapters except the last one as "read"
        for chapter in new_chapters[1:]:
            if chapter.id is not None:
                mark_chapter_as_read(db, chapter.id)
        logger.info('%s: processed %s chapters', manga.title, len(new_chapters[1:]))
