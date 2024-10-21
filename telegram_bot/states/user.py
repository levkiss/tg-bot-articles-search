from aiogram.fsm.state import State, StatesGroup


class UserMainMenu(StatesGroup):
    menu = State()
    language = State()
    daily = State()
    weekly = State()
    article = State()
    article_view = State()

class UserLanguageSelection(StatesGroup):
    selecting = State()
