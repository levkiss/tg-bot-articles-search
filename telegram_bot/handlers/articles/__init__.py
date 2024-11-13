from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram_dialog import setup_dialogs

from .article_dialog import dialog, start, search_article, set_language

def setup_article_handlers() -> Router:
    """
    Set up the router for article handlers
    Args:
        None
    Returns:
        Router: Configured router for article handlers
    """
    router = Router()
    router.include_router(dialog)
    router.message.register(start, CommandStart())
    router.message.register(search_article, Command("new_papers"))
    router.message.register(set_language, Command("language_selection"))
    setup_dialogs(router)
    return router