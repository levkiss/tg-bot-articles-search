"""Module containing prompts for OpenAI interactions."""

from enum import Enum
from typing import Dict


class Language(Enum):
    """Supported languages for summaries."""
    EN = "english"
    RU = "russian"


ARTICLE_SUMMARY_PROMPTS: Dict[Language, str] = {
    Language.EN: """You are a helpful AI research assistant. Please provide a clear and concise summary of the following research paper abstract in English. Focus on:
1. The main problem or goal
2. Key methodology or approach
3. Main results or findings

Keep the summary under 250 words and use simple, clear language.

Abstract:
{abstract}
""",
    Language.RU: """Вы - полезный ИИ-ассистент исследователя. Пожалуйста, предоставьте четкое и краткое резюме следующего научного абстракта на русском языке. Сфокусируйтесь на:
1. Основная проблема или цель
2. Ключевая методология или подход
3. Основные результаты или выводы

Сохраняйте резюме в пределах 250 слов и используйте простой, понятный язык.

Абстракт:
{abstract}
"""
}

SYSTEM_PROMPTS: Dict[Language, str] = {
    Language.EN: "You are a helpful AI research assistant, skilled at summarizing complex academic papers in clear, concise English language.",
    Language.RU: "Вы - полезный ИИ-ассистент исследователя, умеющий кратко и четко излагать сложные научные статьи на русском языке."
}

