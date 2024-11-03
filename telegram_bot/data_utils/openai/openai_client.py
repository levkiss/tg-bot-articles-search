"""Module for handling interactions with OpenAI API."""

import asyncio
from typing import Dict, Optional, Any, List, Union
import logging

from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from telegram_bot.data_utils.openai.prompts import (
    ARTICLE_SUMMARY_PROMPTS,
    SYSTEM_PROMPTS,
    Language
)


class OpenAIError(Exception):
    """Base exception for OpenAI-related errors."""
    pass


class OpenAIRateLimitError(OpenAIError):
    """Exception for rate limit errors."""
    pass


class OpenAITimeoutError(OpenAIError):
    """Exception for timeout errors."""
    pass


class OpenAIClient:
    """Class for managing interactions with OpenAI API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 500,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model to use for completions
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            logger: Optional logger instance

        Raises:
            ValueError: If temperature is not in valid range
        """
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = logger or logging.getLogger(__name__)

    @retry(
        retry=retry_if_exception_type((APIError, RateLimitError, APITimeoutError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(3)
    )
    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """
        Make request to OpenAI API with retry logic.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters for completion

        Returns:
            str: Response content

        Raises:
            OpenAIRateLimitError: If rate limit is exceeded
            OpenAITimeoutError: If request times out
            OpenAIError: For other API errors
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            return response.choices[0].message.content

        except RateLimitError as e:
            self.logger.error(f"Rate limit exceeded: {e}")
            raise OpenAIRateLimitError(f"Rate limit exceeded: {e}")
        except APITimeoutError as e:
            self.logger.error(f"Request timed out: {e}")
            raise OpenAITimeoutError(f"Request timed out: {e}")
        except APIError as e:
            self.logger.error(f"API error occurred: {e}")
            raise OpenAIError(f"API error occurred: {e}")

    async def summarize_paper(
        self,
        abstract: str,
        languages: Optional[List[Language]] = None,
        custom_prompts: Optional[Dict[Language, str]] = None,
        **kwargs: Any
    ) -> Dict[Language, str]:
        """
        Generate summaries of a paper abstract in specified languages.

        Args:
            abstract: Paper abstract text
            languages: List of languages to generate summaries in (defaults to [EN, RU])
            custom_prompts: Optional dictionary of custom prompts by language
            **kwargs: Additional parameters for completion (temperature, max_tokens)

        Returns:
            Dict[Language, str]: Dictionary mapping languages to their summaries

        Raises:
            OpenAIError: If API request fails
            ValueError: If abstract is empty or invalid language specified
        """
        if not abstract:
            raise ValueError("Abstract cannot be empty")

        languages = languages or [Language.EN, Language.RU]
        summaries = {}

        for lang in languages:
            try:
                prompt = (custom_prompts or {}).get(lang) or ARTICLE_SUMMARY_PROMPTS[lang]
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPTS[lang]},
                    {"role": "user", "content": prompt.format(abstract=abstract)}
                ]
                summaries[lang] = await self._make_request(messages, **kwargs)
            except Exception as e:
                self.logger.error(f"Error generating {lang.value} summary: {e}")
                raise OpenAIError(f"Error generating {lang.value} summary: {e}")

        return summaries


if __name__ == "__main__":
    import os
    import asyncio
    
    async def main():
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize client
        client = OpenAIClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )
        
        # Test abstract
        test_abstract = """
        We introduce a novel approach to language modeling that leverages deep learning
        architectures to improve performance on complex NLP tasks. Our model achieves
        state-of-the-art results on multiple benchmarks while using fewer parameters
        than existing approaches.
        """
        
        try:
            summaries = await client.summarize_paper(
                test_abstract,
                languages=[Language.EN, Language.RU]
            )
            print("\nEnglish summary:")
            print(summaries[Language.EN])
            print("\nRussian summary:")
            print(summaries[Language.RU])
        except OpenAIError as e:
            print(f"Error: {e}")

    asyncio.run(main())