from aiogram.filters.state import State, StatesGroup
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Back, Url
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram.filters import CommandStart
from aiogram import F

from telegram_bot.states.article import ArticleSG
from .article_handlers import actions, previous_article, next_article, read_full_article, back_to_abstract

# Dialog definition
dialog = Dialog(
    Window(
        Const("Click find article to show a list of available articles:"),
        SwitchTo(Const("Find article"), id="search", state=ArticleSG.abstract),
        state=ArticleSG.main,
    ),
    Window(
        Format("Searching results: \n{title} \n\n{abstract}"),
        # Const("Search did not return any results", when=~F["articles"]),
        Row(
            Button(Const("◀️ Previous article"), id="previous_article", on_click=previous_article),
            Button(Const("Next article ▶️"), id="next_article", on_click=next_article),
        ),
        # Button(Const("Read full article"), id="read_full_article", on_click=read_full_article),
        SwitchTo(Const("Read full article"), id="read_full_article", state=ArticleSG.summary),
        Url(Format("Link to article"), Format("{url}"), id="url"),
        Back(Const("Back to main menu")),
        state=ArticleSG.abstract,
        getter=actions,
    ),
    Window(
        Format("Searching results: \n{title} \n\n{summary}"),
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