import asyncpg
import structlog
from typing import List, Dict, Any

from telegram_bot.db.db_api.storages.postgres import PostgresConnection

class DatabaseManager(PostgresConnection):
    def __init__(
        self,
        connection_pool: asyncpg.Pool,
        logger: structlog.typing.FilteringBoundLogger,
    ):
        super().__init__(connection_pool, logger)
        self.initialize_tables()

    async def initialize_tables(self):
        """
        Check if required tables exist and create them if they don't.
        """
        await self._create_summaries_table()

    async def _create_summaries_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS summaries (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            snippet TEXT NOT NULL,
            link TEXT NOT NULL,
            embedding VECTOR(1536),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self._execute(create_table_query)

    async def store_paper(self, title: str, snippet: str, link: str, embedding: List[float]):
        """
        Store a paper in the database.

        Args:
            title (str): The paper's title.
            snippet (str): A snippet or abstract of the paper.
            link (str): The link to the paper.
            embedding (List[float]): The paper's embedding vector.
        """
        query = """
        INSERT INTO summaries (title, snippet, link, embedding)
        VALUES ($1, $2, $3, $4)
        """
        await self._execute(query, (title, snippet, link, embedding))

    async def get_similar_papers(self, embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve papers similar to the given embedding.

        Args:
            embedding (List[float]): The query embedding.
            top_k (int): The number of similar papers to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of similar papers.
        """
        query = """
        SELECT title, snippet, link, embedding <-> $1 AS distance
        FROM summaries
        ORDER BY distance
        LIMIT $2
        """
        results = await self._fetch(query, (embedding, top_k))
        return [
            {
                'title': row['title'],
                'snippet': row['snippet'],
                'link': row['link'],
                'similarity': 1 - row['distance']
            }
            for row in results
        ]

    async def get_recent_papers(self, limit: int = 20) -> List[Dict[str, str]]:
        """
        Retrieve the most recent papers.

        Args:
            limit (int): The number of papers to retrieve.

        Returns:
            List[Dict[str, str]]: A list of recent papers.
        """
        query = """
        SELECT title, snippet, link
        FROM summaries
        ORDER BY created_at DESC
        LIMIT $1
        """
        results = await self._fetch(query, (limit,))
        return [
            {
                'title': row['title'],
                'snippet': row['snippet'],
                'link': row['link']
            }
            for row in results
        ]