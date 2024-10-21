import aiogram.types
from ..consts import InlineConstructor

class ArticleInlineButtons(InlineConstructor):
    @staticmethod
    def navigation() -> aiogram.types.InlineKeyboardMarkup:
        schema = [2]
        btns = [
            {"text": "◀️ Предыдущая статья", "callback_data": "previous_article"},
            {"text": "Следующая статья ▶️", "callback_data": "next_article"},
        ]
        return ArticleInlineButtons._create_kb(btns, schema)

    @staticmethod
    def abstract_and_link() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [
            {"text": "🔙 Абстракт", "callback_data": "article_abstract"},
            {"text": "🔗 Перейти по ссылке", "callback_data": "article_link"},
        ]
        return ArticleInlineButtons._create_kb(btns, schema)
    
    @staticmethod
    def overview_and_link() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [
            {"text": "📄 Обзор статьи", "callback_data": "article_overview"},
            {"text": "🔗 Перейти по ссылке", "callback_data": "article_link"},
        ]
        return ArticleInlineButtons._create_kb(btns, schema)

    @staticmethod
    def menu() -> aiogram.types.InlineKeyboardMarkup:
        # Combine navigation and overview/link buttons
        navigation_kb = ArticleInlineButtons.navigation()
        overview_kb = ArticleInlineButtons.overview_and_link()
        return aiogram.types.InlineKeyboardMarkup(inline_keyboard=navigation_kb.inline_keyboard + overview_kb.inline_keyboard)
    
    @staticmethod
    def article_detailed_info() -> aiogram.types.InlineKeyboardMarkup:
        # Combine navigation and overview/link buttons
        navigation_kb = ArticleInlineButtons.navigation()
        overview_kb = ArticleInlineButtons.abstract_and_link()
        return aiogram.types.InlineKeyboardMarkup(inline_keyboard=navigation_kb.inline_keyboard + overview_kb.inline_keyboard)