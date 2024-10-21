from aiogram.utils.formatting import Bold
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Back, Url
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram.filters import CommandStart
from aiogram import F

from telegram_bot.states.article import ArticleSG
from .article_handlers import actions, previous_article, next_article, read_article_summary, back_to_abstract


dialog = Dialog(
    Window(
        Const("Welcome to your daily dose of knowledge! Click <b>Show Daily Articles</b> to explore the latest and greatest articles curated just for you."),
        SwitchTo(Const("Show Daily Articles"), id="search", state=ArticleSG.abstract),
        state=ArticleSG.main,
    ),
    Window(
        Format("{html_text}"),
        Row(
            Button(Const("◀️ Previous article"), id="previous_article", on_click=previous_article),
            Button(Const("Next article ▶️"), id="next_article", on_click=next_article),
        ),
        SwitchTo(Const("Read article summary"), id="read_article_summary", state=ArticleSG.summary),
        Url(Format("Link to article"), Format("{url}"), id="url"),
        Back(Const("Back to main menu")),
        state=ArticleSG.abstract,
        getter=actions,
    ),
    Window(
        Format("{html_text}"), # parse_mode="HTML"),
        # Const("Search did not return any results", when=~F["articles"]),
        Row(
            Button(Const("◀️ Previous article"), id="previous_article", on_click=previous_article),
            Button(Const("Next article ▶️"), id="next_article", on_click=next_article),
        ),
        SwitchTo(Const("Back to abstract"), id="back_to_abstract", state=ArticleSG.abstract),
        Url(Format("Link to article"), Format("{url}"), id="url"),
        Back(Const("Back to main menu")),
        state=ArticleSG.summary,
        getter=actions,
    ),
)

async def start(message: Message, dialog_manager: DialogManager) -> None:
    """
    Args:
        message (Message): Incoming message
        dialog_manager (DialogManager): Dialog manager instance
    Returns:
        None
    """
    await dialog_manager.start(ArticleSG.main, mode=StartMode.RESET_STACK)