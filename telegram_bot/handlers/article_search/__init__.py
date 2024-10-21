from aiogram import Router
from aiogram.filters import CommandStart
from aiogram_dialog import setup_dialogs

from .article_dialog import dialog, start

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
    setup_dialogs(router)
    return router