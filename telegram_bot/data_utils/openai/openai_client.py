import asyncio
from openai import OpenAI
from typing import List, Dict

class OpenAIClient:
    """
    A class to handle interactions with the OpenAI API.
    """

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI client.
        """
        self.client = OpenAI(api_key=api_key)

    async def get_embedding(self, text: str, model: str = "text-embedding-3-small", max_tokens: int = 8000) -> List[float]:
        """
        Get the embedding for the given text.

        Args:
            text (str): The input text.
            model (str): The model to use for embedding.
            max_tokens (int): Maximum number of tokens.

        Returns:
            List[float]: The embedding vector.
        """
        text = text.replace("\n", " ")
        truncated_text = ' '.join(text.split()[:max_tokens])
        
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                input=[truncated_text],
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []

    async def generate_chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini") -> str:
        """
        Generate a chat completion using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): The conversation messages.
            model (str): The model to use for chat completion.

        Returns:
            str: The generated response.
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating chat completion: {e}")
            return ""