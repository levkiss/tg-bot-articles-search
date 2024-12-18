import logging
import asyncio
import aiohttp
import ssl
from datetime import datetime
from typing import List, Dict, Optional

class HuggingFaceAPI:
    """
    An asynchronous class for interacting with the Hugging Face API.
    """

    def __init__(self):
        self.base_url = "https://huggingface.co/api"
        self.papers_endpoint = f"{self.base_url}/daily_papers"
        self.papers_data: List[Dict[str, str]] = []
        self.logger = logging.getLogger(__name__)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def get_markdown_content(self, url: str) -> Optional[str]:
        """
        Get the markdown content from the given URL.

        Args:
            url (str): The URL of the paper.

        Returns:
            Optional[str]: The markdown content of the paper or None if the content is not found.
        """
        full_url = f"https://r.jina.ai/{url}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url, ssl=self.ssl_context) as response:
                    response.raise_for_status()
                    return await response.text()
        except aiohttp.ClientError as e:
            self.logger.error(f"Failed to retrieve markdown content from {full_url}: {e}")
            return None

    async def get_paper_content(self, paper_url: str) -> Optional[str]:
        """
        Get the abstract from the given paper URL.


        Args:
            paper_url (str): The URL of the paper.

        Returns:
            Optional[str]: The abstract of the paper or None if the abstract is not found.
        """
        try:
            markdown_content = await self.get_markdown_content(paper_url)
            if markdown_content is None:
                self.logger.error(f"Failed to retrieve markdown content for {paper_url}")
                return None

            # Now, we need to extract the abstract from the markdown content
            # Let's assume that the abstract is under the '## Abstract' heading
            abstract = ""
            lines = markdown_content.split('\n')
            in_abstract = False
            for line in lines:
                if '## Abstract' in line:
                    in_abstract = True
                    continue
                elif line.startswith('## ') and in_abstract:
                    # Reached the next section
                    break
                elif in_abstract:
                    abstract += line + '\n'
            if abstract.strip() == "":
                # If no abstract found, use the entire markdown content as fallback
                abstract = markdown_content
            return abstract.strip()
        except Exception as e:
            self.logger.error(f"An error occurred while processing the paper content from {paper_url}: {e}")
            return None

    async def fetch_papers_for_date(self, date_str: str) -> List[Dict[str, str]]:
        """
        Asynchronously fetches papers for a specific date from the Hugging Face API.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format (e.g., "2024-10-31")
        
        Returns:
            List[Dict[str, str]]: List of processed papers data
        """
        try:
            url = f"{self.papers_endpoint}?date={date_str}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=self.ssl_context) as response:
                    response.raise_for_status()
                    raw_data = await response.json()
                
                tasks = []
                for paper_data in raw_data:
                    tasks.append(self.process_paper(session, paper_data))
                
                papers_data = await asyncio.gather(*tasks)
            
            self.logger.info(f"Successfully fetched and processed {len(papers_data)} papers for date {date_str}")
            return papers_data
        except aiohttp.ClientError as e:
            self.logger.error(f"Error fetching papers for date {date_str}: {e}")
            return []

    async def fetch_daily_papers(self) -> None:
        """
        Wrapper method to fetch today's papers.
        """
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        await self.fetch_papers_for_date(today)

    async def process_paper(self, session: aiohttp.ClientSession, paper_data: Dict) -> Dict[str, str]:
        """
        Processes a single paper by extracting relevant information.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for requests
            paper_data (Dict): The raw paper data from the API

        Returns:
            Dict[str, str]: A dictionary containing the paper's URL, title, authors, abstract, and other relevant information
        """
        paper_id = paper_data['paper']['id']
        paper_url = f"https://arxiv.org/pdf/{paper_id}"
        
        # Extract authors
        authors = ", ".join([author['name'] for author in paper_data['paper']['authors'] if not author.get('hidden', False)])

        return {
            'id': paper_id,
            'url': paper_url,
            'title': paper_data['paper']['title'],
            'authors': authors,
            'abstract': paper_data['paper']['summary'],
            'paper_published_at': datetime.strptime(paper_data['paper']['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            'published_at': datetime.strptime(paper_data['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            'upvotes': str(paper_data['paper']['upvotes']),
            'num_comments': str(paper_data.get('numComments', 0)),
            'thumbnail': paper_data.get('thumbnail', ''),
            'media_urls': ", ".join(paper_data.get('mediaUrls', [])),
            'submitted_by': paper_data['submittedBy']['fullname']
        }

    async def get_paper_abstract(self, session: aiohttp.ClientSession, paper_id: str) -> Optional[str]:
        """
        Asynchronously retrieves the abstract of a specific paper.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for requests
            paper_id (str): The ID of the paper

        Returns:
            Optional[str]: The abstract of the paper, or None if not found
        """
        try:
            paper_url = f"{self.base_url}/papers/{paper_id}"
            async with session.get(paper_url, ssl=self.ssl_context) as response:
                response.raise_for_status()
                paper_data = await response.json()
            abstract = paper_data.get('summary')
            if abstract:
                self.logger.info(f"Successfully retrieved abstract for paper {paper_id}")
                return abstract
            else:
                self.logger.warning(f"No abstract found for paper {paper_id}")
                return None
        except aiohttp.ClientError as e:
            self.logger.error(f"Error retrieving abstract for paper {paper_id}: {e}")
            return None

# if __name__ == "__main__":
#     async def main():
#         huggingface_api = HuggingFaceAPI()
#         await huggingface_api.fetch_daily_papers()
        
#         # Print the first paper's data as an example
#         if huggingface_api.papers_data:
#             print(huggingface_api.papers_data[0])
#         else:
#             print("No papers fetched.")

#     asyncio.run(main())