from aiogram.fsm.state import State, StatesGroup


class ArticleSG(StatesGroup):
    language = State()
    main_english = State()
    main_russian = State()
