"""Module for managing HuggingFace papers and their summaries."""
import asyncio

from datetime import datetime
from typing import Optional, List, Dict, Tuple, Union

from telegram_bot.data_utils.huggingface.huggingface_db import HuggingFaceDB
from telegram_bot.data_utils.openai import get_openai_client, Language, OpenAIError


class HuggingFaceManager:
    """Class for managing HuggingFace papers and their summaries."""

    def __init__(self, db_connection) -> None:
        """
        Initialize HuggingFace manager.

        Args:
            db_connection: Database connection instance
        """
        self.hf_db = HuggingFaceDB(db_connection)
        self.openai_client = get_openai_client()

    async def init_summaries_table(self) -> None:
        """
        Create summaries table if it doesn't exist.

        Args:
            None

        Returns:
            None
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS paper_summaries (
            paper_id TEXT PRIMARY KEY,
            summary_en TEXT,
            summary_ru TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES papers (id)
        );
        """
        await self.hf_db.db._execute(create_table_sql)

    async def save_summary(
        self,
        paper_id: str,
        summaries: Dict[Language, str]
    ) -> None:
        """
        Save paper summaries to database.

        Args:
            paper_id: Paper ID
            summaries: Dictionary with summaries in different languages

        Returns:
            None
        """
        insert_sql = """
        INSERT INTO paper_summaries (paper_id, summary_en, summary_ru)
        VALUES ($1, $2, $3)
        ON CONFLICT (paper_id) DO UPDATE 
        SET summary_en = $2, summary_ru = $3;
        """
        params = (
            paper_id,
            summaries.get(Language.EN),
            summaries.get(Language.RU)
        )
        await self.hf_db.db._execute(insert_sql, params)

    async def get_paper_summary(self, paper_id: str) -> Optional[Dict[Language, str]]:
        """
        Get paper summaries from database.

        Args:
            paper_id: Paper ID

        Returns:
            Optional[Dict[Language, str]]: Dictionary with summaries or None if not found
        """
        sql = """
        SELECT summary_en, summary_ru 
        FROM paper_summaries 
        WHERE paper_id = $1;
        """
        result = await self.hf_db.db._fetchrow(sql, (paper_id,))
        if result.data:
            return {
                Language.EN: result.data['summary_en'],
                Language.RU: result.data['summary_ru']
            }
        return None

    async def create_summaries_for_paper(
        self,
        paper_id: str,
        abstract: str
    ) -> Dict[Language, str]:
        """
        Create summaries for a paper using OpenAI.

        Args:
            paper_id: Paper ID
            abstract: Paper abstract

        Returns:
            Dict[Language, str]: Dictionary with summaries
        """
        try:
            summaries = await self.openai_client.summarize_paper(abstract)
            await self.save_summary(paper_id, summaries)
            return summaries
        except OpenAIError as e:
            self.hf_db.logger.error(f"Error creating summaries for paper {paper_id}: {e}")
            raise

    async def sync_papers_and_summaries(self) -> None:
        """
        Sync papers and create summaries for new papers.

        Args:
            None

        Returns:
            None
        """
        # Initialize tables
        await self.hf_db.init_db()
        await self.init_summaries_table()

        # Sync papers
        await self.hf_db.sync_papers()

        # Get papers without summaries
        sql = """
        SELECT p.id, p.abstract 
        FROM papers p 
        LEFT JOIN paper_summaries ps ON p.id = ps.paper_id 
        WHERE ps.paper_id IS NULL;
        """
        result = await self.hf_db.db._fetch(sql)
        
        # Create summaries for new papers
        tasks = []
        for paper in result.data:
            tasks.append(self.create_summaries_for_paper(paper['id'], paper['abstract']))
        
        for task in asyncio.as_completed(tasks):
            try:
                await task
            except Exception as e:
                self.hf_db.logger.error(f"Error processing paper: {e}")
                continue

    async def get_paper_info(
        self,
        paper_id: str,
        lang: str = "en"
    ) -> Optional[Dict[str, str]]:
        """
        Get paper information including summary in selected language.

        Args:
            paper_id: Paper ID
            lang: Language code ("en" or "ru", default: "en")

        Returns:
            Optional[Dict[str, str]]: Paper information or None if not found
            Dictionary contains:
                - title: Paper title
                - authors: Paper authors
                - url: Paper URL
                - summary: Paper summary in selected language

        Raises:
            ValueError: If language code is not supported
        """
        # Validate language
        try:
            language = Language.EN if lang.lower() == "en" else Language.RU
        except ValueError:
            raise ValueError(f"Unsupported language code: {lang}. Use 'en' or 'ru'")

        sql = """
        SELECT 
            p.title,
            p.authors,
            p.url,
            CASE 
                WHEN $2 = 'en' THEN ps.summary_en 
                ELSE ps.summary_ru 
            END as summary
        FROM papers p
        LEFT JOIN paper_summaries ps ON p.id = ps.paper_id
        WHERE p.id = $1;
        """
        
        result = await self.hf_db.db._fetchrow(sql, (paper_id, lang.lower()))
        
        if not result.data:
            return None

        return {
            'title': result.data['title'],
            'authors': result.data['authors'],
            'url': result.data['url'],
            'summary': result.data['summary']
        }

    async def get_latest_papers(
        self,
        limit: int = 10,
        lang: str = "en"
    ) -> List[Dict[str, str]]:
        """
        Get latest papers with summaries.

        Args:
            limit: Maximum number of papers to return (default: 10)
            lang: Language code ("en" or "ru", default: "en")

        Returns:
            List[Dict]: List of paper information with summaries in requested language
        """
        sql = """
        SELECT 
            p.id,
            p.title,
            p.authors,
            p.url,
            CASE 
                WHEN $2 = 'en' THEN ps.summary_en 
                ELSE ps.summary_ru 
            END as summary
        FROM papers p
        LEFT JOIN paper_summaries ps ON p.id = ps.paper_id
        ORDER BY p.published_at DESC
        LIMIT $1;
        """
        
        result = await self.hf_db.db._fetch(sql, (limit, lang.lower()))
        
        return [{
            'id': paper['id'],
            'title': paper['title'],
            'authors': paper['authors'],
            'url': paper['url'],
            'summary': paper['summary']
        } for paper in result.data]


# if __name__ == "__main__":
#     import asyncio
#     import os
#     import structlog
#     import logging
#     from telegram_bot.db.db_api.storages.postgres import PostgresConnection
#     import asyncpg

#     async def main():
#         # Configure logging
#         logging.basicConfig(
#             level=logging.INFO,
#             format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#         )
        
#         # Setup structlog
#         structlog.configure(
#             wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
#         )
#         logger = structlog.get_logger()

#         # Create connection pool
#         pool = await asyncpg.create_pool(
#             host=os.getenv("POSTGRES_HOST", "localhost"),
#             port=int(os.getenv("POSTGRES_PORT", 5432)),
#             user=os.getenv("POSTGRES_USER", "postgres"),
#             password=os.getenv("POSTGRES_PASSWORD", "postgres"),
#             database=os.getenv("POSTGRES_DB", "papers_db")
#         )

#         try:
#             # Initialize manager
#             db = PostgresConnection(pool, logger)
#             manager = HuggingFaceManager(db)

#             # Sync papers and create summaries
#             print("Syncing papers and creating summaries...")
#             await manager.sync_papers_and_summaries()

#             # Get latest papers
#             papers = await manager.get_latest_papers(3)
#             print("\nLatest papers:")
#             for paper in papers:
#                 print(f"\nTitle: {paper['title']}")
#                 print(f"Authors: {paper['authors']}")
#                 print(f"URL: {paper['url']}")
#                 print("English summary:", paper['summaries'][Language.EN])
#                 print("Russian summary:", paper['summaries'][Language.RU])

#         finally:
#             await pool.close()

#     asyncio.run(main())
