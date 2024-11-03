from typing import Dict, Any, List, Optional
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button

from telegram_bot.states.article import ArticleSG
from telegram_bot.data_utils.huggingface import get_huggingface_manager

class ArticleState:
    """Class to store global state"""
    def __init__(self):
        self.manager = None
        self.articles: List[Dict[str, Any]] = []
        self.current_language: str = "en"

# Global state
state = ArticleState()

async def language_selected(c: CallbackQuery, button: Button, manager: DialogManager):
    """
    Handle language selection and initialize articles in selected language.
    
    Args:
        c: Callback query
        button: Button widget that triggered the callback
        manager: Dialog manager instance
    """
    # Get language from button widget_id
    language = button.widget_id  # will be "ru" or "en"
    manager.dialog_data["language"] = language
    manager.dialog_data["index"] = 0  # Reset index when language changes
    
    # Initialize manager if needed
    if state.manager is None:
        state.manager = await get_huggingface_manager()
    
    # Get fresh articles in selected language
    state.articles = await state.manager.get_latest_papers(limit=10, lang=language)
    state.current_language = language
    
    await c.answer()
    print(f"Language selected: {language}")
    await manager.switch_to(ArticleSG.main_english if language == "en" else ArticleSG.main_russian)

async def get_article_by_index(index: int) -> Dict[str, Any]:
    """
    Get article information by index.
    
    Args:
        index: Index of the article in the articles list
    
    Returns:
        Dict[str, Any]: Article information including title, authors, summary, etc.
    """
    if not state.articles:
        return {
            "index": 0,
            "id": "",
            "title": "Please select a language first",
            "authors": "",
            "summary": "Use the language selector above",
            "url": "",
        }
    
    # Ensure index is within bounds
    index = max(0, min(index, len(state.articles) - 1))
    article = state.articles[index]
    
    return {
        "index": index,
        "id": article["id"],
        "title": article["title"],
        "authors": article["authors"],
        "summary": article["summary"],
        "url": article["url"],
    }

async def actions(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Get article information for current index.
    
    Args:
        dialog_manager: Dialog manager instance
        **kwargs: Additional keyword arguments
    
    Returns:
        Dict[str, Any]: Article information for display
    """
    index = dialog_manager.dialog_data.get("index", 0)
    article = await get_article_by_index(index)

    html_text = (
        f"<b>{article['title']}</b>\n\n"
        f"{article['summary']}"
    )

    return {**article, "html_text": html_text}

async def previous_article(c: CallbackQuery, b: Button, dialog_manager: DialogManager) -> None:
    """
    Handle navigation to previous article.
    
    Args:
        c: Callback query
        b: Button widget
        dialog_manager: Dialog manager instance
    """
    index = dialog_manager.dialog_data.get("index", 0)
    if state.articles:
        dialog_manager.dialog_data["index"] = index - 1 if index > 0 else len(state.articles) - 1
    await dialog_manager.switch_to(ArticleSG.main_english if state.current_language == "en" else ArticleSG.main_russian)

async def next_article(c: CallbackQuery, b: Button, dialog_manager: DialogManager) -> None:
    """
    Handle navigation to next article.
    
    Args:
        c: Callback query
        b: Button widget
        dialog_manager: Dialog manager instance
    """
    index = dialog_manager.dialog_data.get("index", 0)
    if state.articles:
        dialog_manager.dialog_data["index"] = index + 1 if index < len(state.articles) - 1 else 0
    await dialog_manager.switch_to(ArticleSG.main_english if state.current_language == "en" else ArticleSG.main_russian)