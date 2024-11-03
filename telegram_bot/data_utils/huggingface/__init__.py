"""
Initialization module for HuggingFace manager.
Provides convenient factory function to create HuggingFace manager instances.
"""

from typing import Optional
import logging
import structlog
import asyncpg

from telegram_bot.data import config
from telegram_bot.db.db_api.storages.postgres import PostgresConnection
from telegram_bot.data_utils.huggingface.huggingface_manager import HuggingFaceManager


async def get_huggingface_manager(
    db_pool: Optional[asyncpg.Pool] = None,
    logger: Optional[logging.Logger] = None
) -> HuggingFaceManager:
    """
    Factory function to create an initialized HuggingFace manager.

    Args:
        db_pool: Optional existing database pool
        logger: Optional logger instance

    Returns:
        HuggingFaceManager: Initialized HuggingFace manager instance

    Raises:
        ValueError: If database connection cannot be established
        ConnectionError: If database connection fails
    """
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Setup structlog
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )

        # Use provided logger or create new one
        log = logger or structlog.get_logger()

        # Use provided pool or create new one
        if not db_pool:
            db_pool = await asyncpg.create_pool(
                host=config.POSTGRES_HOST,
                port=config.POSTGRES_PORT,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD,
                database=config.POSTGRES_DB
            )
            if not db_pool:
                raise ConnectionError("Failed to create database pool")

        # Initialize PostgresConnection
        db_connection = PostgresConnection(
            connection_poll=db_pool,
            logger=log
        )

        # Create and return manager instance
        manager = HuggingFaceManager(db_connection)
        
        # Initialize database tables
        await manager.hf_db.init_db()
        await manager.sync_papers_and_summaries()

        return manager

    except asyncpg.PostgresError as e:
        raise ConnectionError(f"Database connection error: {e}")
    except Exception as e:
        raise ValueError(f"Failed to initialize HuggingFace manager: {e}")


# Export necessary classes and functions for convenient imports
from telegram_bot.data_utils.huggingface.huggingface_manager import HuggingFaceManager
from telegram_bot.data_utils.huggingface.huggingface_db import HuggingFaceDB

__all__ = [
    'get_huggingface_manager',
    'HuggingFaceManager',
    'HuggingFaceDB'
]