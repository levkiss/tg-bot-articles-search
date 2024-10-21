from telegram_bot.data_utils.huggingface import HuggingFaceAPI
from telegram_bot.data_utils.openai import OpenAIClient
from telegram_bot.data_utils.papers.database_manager import DatabaseManager
from typing import List, Dict

class PapersManager:
    """
    A class to manage paper-related operations.
    """

    def __init__(self, huggingface_api: HuggingFaceAPI, openai_client: OpenAIClient, db_manager: DatabaseManager):
        """
        Initialize the PapersManager.

        Args:
            huggingface_api (HuggingFaceAPI): An instance of the HuggingFaceAPI.
            openai_client (OpenAIClient): An instance of the OpenAIClient.
            db_manager (DatabaseManager): An instance of the DatabaseManager.
        """
        self.huggingface_api = huggingface_api
        self.openai_client = openai_client
        self.db_manager = db_manager

    async def fetch_and_store_papers(self):
        """
        Fetch papers from HuggingFace API and store them in the database.
        """
        await self.huggingface_api.fetch_daily_papers()
        for paper in self.huggingface_api.papers_data:
            embedding = await self.openai_client.get_embedding(paper['abstract'])
            await self.db_manager.store_paper(paper['title'], paper['abstract'], paper['url'], embedding)

    async def get_similar_papers(self, query: str) -> List[Dict[str, str]]:
        """
        Get papers similar to the given query.

        Args:
            query (str): The query string.

        Returns:
            List[Dict[str, str]]: A list of similar papers.
        """
        embedding = await self.openai_client.get_embedding(query)
        return await self.db_manager.get_similar_papers(embedding)

    async def get_recent_papers(self, limit: int = 20) -> List[Dict[str, str]]:
        """
        Get the most recent papers.

        Args:
            limit (int): The number of papers to retrieve.

        Returns:
            List[Dict[str, str]]: A list of recent papers.
        """
        return await self.db_manager.get_recent_papers(limit)