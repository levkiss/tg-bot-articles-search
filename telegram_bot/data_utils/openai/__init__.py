"""
Initialization module for OpenAI client.
Provides convenient factory function to create OpenAI client instances.
"""

from typing import Optional
import logging

from telegram_bot.data import config
from telegram_bot.data_utils.openai.openai_client import OpenAIClient


def get_openai_client(
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    logger: Optional[logging.Logger] = None
) -> OpenAIClient:
    """
    Factory function to create an initialized OpenAI client.

    Args:
        model: OpenAI model to use (default: "gpt-4-turbo-preview")
        temperature: Sampling temperature between 0.0 and 2.0 (default: 0.7)
        max_tokens: Maximum tokens in response (default: 1000)
        logger: Optional logger instance

    Returns:
        OpenAIClient: Initialized OpenAI client instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set in config
        ValueError: If temperature is not in valid range
    """
    if not config.OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set in config. "
            "Please set it in your environment variables."
        )

    return OpenAIClient(
        api_key=config.OPENAI_API_KEY,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        logger=logger
    )


# Export necessary classes and enums for convenient imports
from telegram_bot.data_utils.openai.openai_client import (
    OpenAIError,
    OpenAIRateLimitError,
    OpenAITimeoutError
)
from telegram_bot.data_utils.openai.prompts import Language

__all__ = [
    'get_openai_client',
    'OpenAIClient',
    'OpenAIError',
    'OpenAIRateLimitError',
    'OpenAITimeoutError',
    'Language'
]
