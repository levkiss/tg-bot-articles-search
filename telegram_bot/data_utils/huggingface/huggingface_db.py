"""Module for handling HuggingFace papers data storage in PostgreSQL database."""

from datetime import datetime, timedelta, date, timezone
from typing import Optional, List, Dict, Union

from telegram_bot.data_utils.huggingface.huggingface_base import HuggingFaceAPI
from telegram_bot.db.db_api.storages.base import BaseConnection


class HuggingFaceDB(HuggingFaceAPI):
    """Class for managing HuggingFace papers data in PostgreSQL database."""

    def __init__(self, db: BaseConnection) -> None:
        """
        Initialize HuggingFaceDB instance.

        Args:
            db: Database connection instance implementing BaseConnection
        """
        super().__init__()
        self.db = db

    async def init_db(self) -> None:
        """
        Create papers table if it doesn't exist.

        Args:
            None

        Returns:
            None
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            authors TEXT,
            abstract TEXT,
            paper_published_at TIMESTAMP,
            published_at TIMESTAMP,
            upvotes INTEGER,
            num_comments INTEGER,
            thumbnail TEXT,
            media_urls TEXT,
            submitted_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.db._execute(create_table_sql)

    async def get_last_paper_date(self) -> Optional[datetime]:
        """
        Get the most recent paper date from the database.

        Args:
            None

        Returns:
            Optional[datetime]: The date of the most recent paper or None if no papers exist
        """
        sql = """
        SELECT published_at 
        FROM papers 
        ORDER BY published_at DESC 
        LIMIT 1;
        """
        result = await self.db._fetchrow(sql)
        if result.data:
            return result.data['published_at']
        return None

    async def save_papers(self, papers: List[Dict]) -> None:
        """
        Save papers to database.

        Args:
            papers: List of paper dictionaries containing paper details

        Returns:
            None
        """
        if not papers:
            return

        insert_sql = """
        INSERT INTO papers (
            id, url, title, authors, abstract, paper_published_at, published_at,
            upvotes, num_comments, thumbnail, media_urls, 
            submitted_by
        ) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        ON CONFLICT (id) DO NOTHING;
        """

        for paper in papers:
            try:
                params = (
                    paper['id'],
                    paper['url'],
                    paper['title'],
                    paper['authors'],
                    paper['abstract'],
                    paper['paper_published_at'],
                    paper['published_at'],
                    int(paper['upvotes']),
                    int(paper['num_comments']),
                    paper['thumbnail'],
                    paper['media_urls'],
                    paper['submitted_by']
                )
                await self.db._execute(insert_sql, params)
            except Exception as e:
                self.logger.error(f"Error saving paper {paper['id']}: {e}")
                continue

    async def sync_papers(self) -> None:
        """
        Sync papers with the database.
        
        If no papers exist in DB, fetches last 7 days.
        Otherwise, fetches papers from the day after the last paper until today.

        Args:
            None

        Returns:
            None
        """
        await self.init_db()
        
        last_date = await self.get_last_paper_date()
        today = datetime.now()
        
        if not last_date:
            # If no papers in DB, fetch last 7 days
            start_date = today - timedelta(days=7)
        else:
            # If have papers, start from the next day after last paper
            start_date = last_date + timedelta(days=1)

        # Don't fetch future dates
        if start_date > today:
            return

        total_papers = 0
        while start_date <= today:
            date_str = start_date.strftime("%Y-%m-%d")
            papers = await self.fetch_papers_for_date(date_str)  # Get papers from API
            if papers:  # Only try to save if we got papers
                await self.save_papers(papers)  # Save to database
                total_papers += len(papers)
            start_date += timedelta(days=1)
        
        self.logger.info(f"Synced total of {total_papers} papers to database")

    async def get_papers_by_date(self, date_str: str) -> List[Dict]:
        """
        Get papers for specific date from database.

        Args:
            date_str: Date string in format 'YYYY-MM-DD'

        Returns:
            List[Dict]: List of papers published on the specified date
        """
        # Convert string to datetime
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        sql = """
        SELECT * FROM papers 
        WHERE DATE(published_at) = $1
        ORDER BY published_at DESC;
        """
        result = await self.db._fetch(sql, (query_date,))
        return result.data

    async def get_papers_by_date_range(
        self, 
        start_date: str, 
        end_date: str
    ) -> List[Dict]:
        """
        Get papers for date range from database.

        Args:
            start_date: Start date string in format 'YYYY-MM-DD'
            end_date: End date string in format 'YYYY-MM-DD'

        Returns:
            List[Dict]: List of papers published within the specified date range
        """
        # Convert strings to datetime
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        sql = """
        SELECT * FROM papers 
        WHERE DATE(published_at) BETWEEN $1 AND $2
        ORDER BY published_at DESC;
        """
        result = await self.db._fetch(sql, (start, end))
        return result.data


# if __name__ == "__main__":
#     import asyncio
#     import os
#     import asyncpg
#     import structlog
#     import logging
#     from telegram_bot.db.db_api.storages.postgres import PostgresConnection

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
        
#         # Initialize PostgresConnection with pool and logger
#         db = PostgresConnection(
#             connection_poll=pool,
#             logger=logger
#         )
        
#         # Initialize HuggingFaceDB
#         hf_db = HuggingFaceDB(db)
        
#         try:
#             # Sync papers (this will fetch last 7 days if DB is empty)
#             print("Syncing papers...")
#             await hf_db.sync_papers()
            
#             # Example: Get papers for today
#             today = datetime.now().strftime("%Y-%m-%d")
#             papers = await hf_db.get_papers_by_date(today)
#             print(f"\nPapers for {today}:")
#             for paper in papers:
#                 print(f"- {paper['title']}")
            
#             # Example: Get papers for last 3 days
#             end_date = datetime.now()
#             start_date = end_date - timedelta(days=3)
#             papers = await hf_db.get_papers_by_date_range(
#                 start_date.strftime("%Y-%m-%d"),
#                 end_date.strftime("%Y-%m-%d")
#             )
#             print(f"\nPapers from last 3 days: {len(papers)}")

#         finally:
#             # Close the connection pool
#             await pool.close()

#     # Run the example
#     asyncio.run(main())
