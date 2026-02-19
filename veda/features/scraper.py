import requests
from bs4 import BeautifulSoup

class VedaScraper:
    @staticmethod
    def ingest_url(url):
        """Scrapes a URL and returns a summary of its content."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Return first 2000 characters to the LLM for summarizing
            return text[:2000]
        except Exception as e:
            return f"Failed to ingest URL: {str(e)}"
