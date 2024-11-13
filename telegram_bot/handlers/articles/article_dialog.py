from aiogram.utils.formatting import Bold
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Back, Url, Select, Group, Column
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.types import CallbackQuery
from typing import Any

from telegram_bot.states.article import ArticleSG
from .article_handlers import actions, previous_article, next_article, language_selected


dialog = Dialog(
    Window(
        Const("💭 Choose the language in which\nI will make selections and reviews\nof articles\n\n💭 Выберите язык, на котором\nя буду делать подборки и\nобзоры статей"),
        Column(
            Button(Const("🇷🇺 Русский"), id="ru", on_click=language_selected),
            Button(Const("🇬🇧 English"), id="en", on_click=language_selected),
        ),
        state=ArticleSG.language,
    ),
    Window(
        Format("{html_text}"),
        Row(
            Button(Const("◀️ Previous article"), id="previous_article", on_click=previous_article),
            Button(Const("Next article ▶️"), id="next_article", on_click=next_article),
        ),
        Url(text=Const("Link to article"), url=Format("{url}"), id="url"),
        state=ArticleSG.main_english,
        getter=actions,
    ),
    Window(
        Format("{html_text}"),
        Row(
            Button(Const("◀️ Предыдущая статья"), id="previous_article", on_click=previous_article),
            Button(Const("Следующая статья ▶️"), id="next_article", on_click=next_article),
        ),
        Url(text=Const("Ссылка на статью"), url=Format("{url}"), id="url"),
        state=ArticleSG.main_russian,
        getter=actions,
    )
)

async def start(message: Message, dialog_manager: DialogManager) -> None:
    """
    Args:
        message (Message): Incoming message
        dialog_manager (DialogManager): Dialog manager instance
    Returns:
        None
    """
    await dialog_manager.start(ArticleSG.language, mode=StartMode.RESET_STACK)

async def search_article(message: Message, dialog_manager: DialogManager) -> None:
    """
    Handler for /search_article command
    Args:
        message (Message): Incoming message
        dialog_manager (DialogManager): Dialog manager instance
    """
    # Start from main window based on current language
    current_lang = dialog_manager.dialog_data.get("language", "en")
    state = ArticleSG.main_english if current_lang == "en" else ArticleSG.main_russian
    await dialog_manager.start(state, mode=StartMode.RESET_STACK)

async def set_language(message: Message, dialog_manager: DialogManager) -> None:
    """
    Handler for /set_language command
    Args:
        message (Message): Incoming message
        dialog_manager (DialogManager): Dialog manager instance
    """
    # Start from language selection window
    await dialog_manager.start(ArticleSG.language, mode=StartMode.RESET_STACK)