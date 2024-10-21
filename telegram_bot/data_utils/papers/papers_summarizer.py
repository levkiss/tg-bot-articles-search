import ast
import aiohttp
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from telegram_bot.data_utils.openai import get_openai_client
from typing import List, Dict

class PapersSummarizer:
    """
    A class to summarize research papers.
    """

    def __init__(self):
        """
        Initialize the PapersSummarizer.
        """
        self.openai_client = get_openai_client()

        # Download necessary NLTK data (you may need to run this once)
        nltk.download('punkt')
        nltk.download('stopwords')
        
    def remove_stopwords(self, text: str) -> str:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
        return ' '.join(filtered_text)

    def get_embedding(self, text: str, model: str = "text-embedding-3-small", max_tokens: int = 8000) -> List[float]:
        text = text.replace("\n", " ")
        
        # First, try removing stopwords
        filtered_text = self.remove_stopwords(text)
        
        # If still too long, truncate
        if len(filtered_text.split()) > max_tokens:
            filtered_text = ' '.join(filtered_text.split()[:max_tokens])
        
        try:
            return openai_client.embeddings.create(input=[filtered_text], model=model).data[0].embedding
        except openai.BadRequestError as e:
            if "maximum context length" in str(e):
                # If still too long, truncate further
                truncated_text = ' '.join(filtered_text.split()[:max_tokens//2])
                return openai_client.embeddings.create(input=[truncated_text], model=model).data[0].embedding
            else:
                raise e
        

    async def summarize_papers(self, papers: List[Dict[str, str]], batch_size: int = 3) -> str:
        """
        Summarize a list of papers in batches.

        Args:
            papers (List[Dict[str, str]]): List of papers to summarize.
            batch_size (int): Number of papers to summarize in each batch.

        Returns:
            str: The overall summary of all papers.
        """
        batches = [papers[i:i+batch_size] for i in range(0, len(papers), batch_size)]
        all_summaries = []

        for batch in batches:
            papers_text = "\n\n".join([f"Title: {paper['title']}\nLink: {paper['link']}" for paper in batch])
            prompt = f"Summarize these {len(batch)} papers concisely, focusing on key findings and applications to low-resource language translation:\n\n{papers_text}"
            
            summary = await self.openai_client.generate_chat_completion([
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ])
            all_summaries.append(summary)

        overall_summary_prompt = f"Provide an overall summary of these recent papers, highlighting important trends and applications for low-resource language translation:\n\n{''.join(all_summaries)}"
        overall_summary = await self.openai_client.generate_chat_completion([
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": overall_summary_prompt}
        ])

        return overall_summary