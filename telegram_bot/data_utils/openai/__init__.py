from .openai_client import OpenAIClient
from telegram_bot.data import config

def get_openai_client() -> OpenAIClient:
    return OpenAIClient(config.OPENAI_API_KEY)
