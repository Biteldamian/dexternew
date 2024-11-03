# toolbox/tools.py
from typing import Dict, Any
from rich.console import Console
import aiohttp
from bs4 import BeautifulSoup

console = Console()

class ToolKit:
    def __init__(self):
        self.session = None
    
    async def initialize(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        if self.session:
            await self.session.close()
    
    async def web_scrape(self, url: str) -> Dict[str, Any]:
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"error": f"HTTP {response.status}"}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                return {
                    "url": url,
                    "content": soup.get_text(strip=True),
                    "title": soup.title.string if soup.title else None
                }
        except Exception as e:
            return {"error": str(e)}