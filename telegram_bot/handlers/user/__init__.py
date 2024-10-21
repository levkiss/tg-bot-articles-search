from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command

from telegram_bot import states
from telegram_bot.filters import ChatTypeFilter, TextFilter

from . import start
from . import select_language


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    # user_router.message.register(start.start, CommandStart())

    # Handler for the /start command
    user_router.message.register(
        select_language.language_selection,
        CommandStart()
    )

    # Register the language selection callback
    user_router.callback_query.register(
        select_language.handle_language_selection,
        StateFilter(states.user.UserLanguageSelection.selecting)
    )

    # Handler to get the selected language
    user_router.message.register(
        select_language.get_selected_language,
        Command("language_selection")
    )
    
    user_router.message.register(
        start.start,
        TextFilter("🏠В главное меню"),  # noqa: RUF001
        StateFilter(states.user.UserMainMenu.menu),
    )

    return user_router
