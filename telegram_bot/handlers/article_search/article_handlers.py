from typing import Dict, Any, List
from aiogram_dialog import DialogManager

from telegram_bot.states.article import ArticleSG

import asyncio
from telegram_bot.data_utils.huggingface import HuggingFaceAPI

# Initialize HuggingFaceAPI
huggingface_api = HuggingFaceAPI()

async def fetch_articles() -> List[Dict[str, Any]]:
    await huggingface_api.fetch_daily_papers()
    return huggingface_api.papers_data

# Get articles
articles: List[Dict[str, Any]] = asyncio.run(fetch_articles())

async def get_article_by_index(index: int) -> Dict[str, Any]:
    """
    Args:
        index (int): Index of the product in the products list
    Returns:
        Dict[str, Any]: Article information
    """
    return {
        "index": index,
        "id": articles[index]["id"],
        "title": articles[index]["title"],
        "authors": articles[index]["authors"],
        "abstract": articles[index]["abstract"],
        "summary": articles[index]["summary"],
        "url": articles[index]["url"],
    }

async def actions(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Args:
        dialog_manager (DialogManager): Dialog manager instance
        **kwargs: Additional keyword arguments
    Returns:
        Dict[str, Any]: Product information for the current index
    """
    index = dialog_manager.dialog_data.get("index", 0)
    article = await get_article_by_index(index)
    state = dialog_manager.current_context().state

    html_text = (
        f"<b>{article['title']}</b>\n\n{article['summary']}"
        if state == ArticleSG.summary
        else f"<b>{article['title']}</b>\n\n{article['abstract']}"
    )

    return {**article, "html_text": html_text}

async def previous_article(c: Any, b: Any, dialog_manager: DialogManager) -> None:
    """
    Args:
        c (Any): Callback query
        b (Any): Button
        dialog_manager (DialogManager): Dialog manager instance
    Returns:
        None
    """
    index = dialog_manager.dialog_data.get("index", 0)
    dialog_manager.dialog_data["index"] = index-1 if index >= 1 else len(articles)-1
    await dialog_manager.switch_to(ArticleSG.abstract)

async def next_article(c: Any, b: Any, dialog_manager: DialogManager) -> None:
    """
    Args:
        c (Any): Callback query
        b (Any): Button
        dialog_manager (DialogManager): Dialog manager instance
    Returns:
        None
    """
    index = dialog_manager.dialog_data.get("index", 0)
    dialog_manager.dialog_data["index"] = index+1 if index < len(articles)-1 else 0
    await dialog_manager.switch_to(ArticleSG.abstract)

async def read_article_summary(c: Any, b: Any, dialog_manager: DialogManager) -> None:
    """
    Args:
        c (Any): Callback query
        b (Any): Button
        dialog_manager (DialogManager): Dialog manager instance
    Returns:
        None
    """
    await dialog_manager.switch_to(ArticleSG.summary)   

async def back_to_abstract(c: Any, b: Any, dialog_manager: DialogManager) -> None:
    """
    Args:
        c (Any): Callback query
        b (Any): Button
        dialog_manager (DialogManager): Dialog manager instance
    Returns:
        None
    """
    await dialog_manager.switch_to(ArticleSG.abstract)  