import os
from typing import Dict, Optional

import telebot
from bson.objectid import ObjectId
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.consts import DB_NAME
from src.database import get_db, get_new_chapters, mark_chapter_as_read
from src.manga_parser import parse_urls
from src.model import MangaChapter

# create bot
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
bot.set_my_commands(
    commands=[
        telebot.types.BotCommand('start', 'Display all buttons'),
        telebot.types.BotCommand('get_last_releases', 'Get last manga releases'),
    ],
)

# connect to db
db = get_db(DB_NAME)


def get_buttons() -> InlineKeyboardMarkup:
    """
    Return main buttons
    """
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('GetLastReleases', callback_data='get_last_releases')
    )
    return markup


def _get_manga_chapters() -> Optional[Dict[str, MangaChapter]]:
    """
    Get new chapters for each manga
    """
    parsed_manga = parse_urls()
    chapters = {}
    for manga in parsed_manga:
        new_chapters = get_new_chapters(db, manga)
        new_chapters = sorted(
            new_chapters, key=lambda chapter: chapter.release_date, reverse=True
        )
        for chapter in new_chapters:
            chapters[f'{manga.title}: {chapter.title}'] = chapter

    return chapters


def _get_last_releases(chat_id: int):
    """
    For each chapter create it's own button
    """
    # get new chapters
    bot.send_message(chat_id, 'Start scraping urls, please wait')
    manga_chapters = _get_manga_chapters()
    # get markups
    markups = []  # (title, markup)
    if manga_chapters is None:
        bot.send_message(chat_id, 'No new chapters')
    else:
        for title, chapter in manga_chapters.items():
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            button_url = InlineKeyboardButton(text='Read manga', url=chapter.url)
            button_mark_as_read = InlineKeyboardButton(
                text='Mark as read', callback_data=f'read_{chapter.id}'
            )
            markup.add(button_url, button_mark_as_read)
            markups.append((title, markup))

        # display markups
        for title, markup in markups:
            bot.send_message(chat_id, title, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'get_last_releases':
        _get_last_releases(call.message.chat.id)
    if call.data.startswith('read_'):
        object_id = ObjectId(call.data.split('_')[1])
        chapter = mark_chapter_as_read(db, object_id)
        if chapter is not None:
            title = f"{chapter['manga_title']}: {chapter['title']}"
            bot.send_message(
                call.message.chat.id,
                f'Marked as read: {title}',
            )
        else:
            bot.send_message(call.message.chat.id, "Didn't find the chapter int the DB")


# Handler for /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Choose an option:', reply_markup=get_buttons())


# Handler for /get_last_releases
@bot.message_handler(commands=['get_last_releases'])
def get_last_releases(message):
    _get_last_releases(message.chat.id)


def app():
    # init bot
    bot.infinity_polling()
