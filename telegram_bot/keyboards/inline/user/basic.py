import aiogram.types
from ..consts import InlineConstructor

class BasicInlineButtons(InlineConstructor):
    @staticmethod
    def back() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "◀️Назад", "callback_data": "back"}]
        return BasicInlineButtons._create_kb(btns, schema)

    @staticmethod
    def cancel() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "🚫 Отмена", "callback_data": "cancel"}]
        return BasicInlineButtons._create_kb(btns, schema)

    @staticmethod
    def back_n_cancel() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [
            {"text": "◀️Назад", "callback_data": "back"},
            {"text": "🚫 Отмена", "callback_data": "cancel"},
        ]
        return BasicInlineButtons._create_kb(btns, schema)

    @staticmethod
    def daily_weekly() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [
            {"text": "Daily", "callback_data": "daily"},
            {"text": "Weekly", "callback_data": "weekly"},
        ]
        return BasicInlineButtons._create_kb(btns, schema)

    @staticmethod
    def confirmation(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.InlineKeyboardMarkup:
        schema = []
        btns = []
        if add_cancel:
            schema.append(1)
            btns.append({"text": "🚫 Отмена", "callback_data": "cancel"})
        schema.append(1)
        btns.append({"text": "✅Подтвердить", "callback_data": "confirm"})
        if add_back:
            schema.append(1)
            btns.append({"text": "◀️Назад", "callback_data": "back"})
        return BasicInlineButtons._create_kb(btns, schema)

    @staticmethod
    def yes(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "✅Да", "callback_data": "yes"}]
        if add_back:
            schema.append(1)
            btns.append({"text": "◀️Назад", "callback_data": "back"})
        if add_cancel:
            schema.append(1)
            btns.append({"text": "🚫 Отмена", "callback_data": "cancel"})
        return BasicInlineButtons._create_kb(btns, schema)

    @staticmethod
    def no(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "❌Нет", "callback_data": "no"}]
        if add_back:
            schema.append(1)
            btns.append({"text": "◀️Назад", "callback_data": "back"})
        if add_cancel:
            schema.append(1)
            btns.append({"text": "🚫 Отмена", "callback_data": "cancel"})
        return BasicInlineButtons._create_kb(btns, schema)

    @staticmethod
    def yes_n_no(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.InlineKeyboardMarkup:
        schema = [2]
        btns = [
            {"text": "✅Да", "callback_data": "yes"},
            {"text": "❌Нет", "callback_data": "no"},
        ]
        if add_back:
            schema.append(1)
            btns.append({"text": "◀️Назад", "callback_data": "back"})
        if add_cancel:
            schema.append(1)
            btns.append({"text": "🚫 Отмена", "callback_data": "cancel"})
        return BasicInlineButtons._create_kb(btns, schema)
    
    @staticmethod
    def language_selection() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [
            {"text": "🇷🇺 Русский", "callback_data": "set_language_russian"},
            {"text": "🇬🇧 English", "callback_data": "set_language_english"},
        ]
        return BasicInlineButtons._create_kb(btns, schema)