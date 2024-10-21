import asyncio
import asyncpg
import structlog
from typing import Dict, Any

from telegram_bot.data import config
from telegram_bot.data_utils.huggingface import HuggingFaceAPI
from telegram_bot.data_utils.openai import get_openai_client
from .database_manager import DatabaseManager
from .papers_manager import PapersManager

async def initialize_database(config: Dict[str, Any]) -> DatabaseManager:
    """
    Initialize the DatabaseManager with the given configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary containing database connection details.

    Returns:
        DatabaseManager: An initialized DatabaseManager instance.
    """
    logger = structlog.get_logger()

    try:
        pool = await asyncpg.create_pool(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_DATABASE,
            min_size=config.DB_MIN_CONNECTIONS,
            max_size=config.DB_MAX_CONNECTIONS,
        )

        db_manager = DatabaseManager(pool, logger)
        await db_manager.initialize_tables()

        logger.info("Database initialized successfully")
        return db_manager

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def close_database(db_manager: DatabaseManager):
    """
    Close the database connection pool.

    Args:
        db_manager (DatabaseManager): The DatabaseManager instance to close.
    """
    await db_manager._pool.close()
    logger = structlog.get_logger()
    logger.info("Database connection closed")


async def get_papers_manager() -> PapersManager:
    """
    Get an instance of the PapersManager.
    """ 
    huggingface_api = HuggingFaceAPI()
    openai_client = get_openai_client()
    db_manager = await initialize_database(config)
    return PapersManager(huggingface_api, openai_client, db_manager)
