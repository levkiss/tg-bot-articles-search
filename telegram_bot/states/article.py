from aiogram.fsm.state import State, StatesGroup


class ArticleSG(StatesGroup):
    main = State()
    abstract = State()
    summary = State()