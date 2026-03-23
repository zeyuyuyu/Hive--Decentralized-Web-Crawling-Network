import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
import redis
import logging

class DistributedCrawler:
    def __init__(self, redis_url: str, max_requests_per_second: int = 10):
        self.redis_client = redis.from_url(redis_url)
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit = max_requests_per_second
        self.request_times: Dict[str, datetime] = {}
        self.seen_urls: Set[str] = set()
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _check_rate_limit(self, domain: str) -> None:
        """Ensure we don't exceed rate limits for a domain"""
        now = datetime.now()
        if domain in self.request_times:
            time_diff = now - self.request_times[domain]
            if time_diff.total_seconds() < (1.0 / self.rate_limit):
                await asyncio.sleep(1.0 / self.rate_limit - time_diff.total_seconds())
        self.request_times[domain] = now

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page with rate limiting and caching"""
        if url in self.seen_urls:
            self.logger.debug(f"Skipping already seen URL: {url}")
            return None

        # Check cache first
        cached_content = self.redis_client.get(f"page:{url}")
        if cached_content:
            self.logger.debug(f"Cache hit for URL: {url}")
            return cached_content.decode('utf-8')

        # Extract domain for rate limiting
        domain = url.split('/')[2]
        await self._check_rate_limit(domain)

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    # Cache the result with 1 hour expiration
                    self.redis_client.setex(
                        f"page:{url}",
                        timedelta(hours=1),
                        content.encode('utf-8')
                    )
                    self.seen_urls.add(url)
                    return content
                else:
                    self.logger.warning(f"Failed to fetch {url}: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    async def crawl_urls(self, urls: list[str]) -> Dict[str, Optional[str]]:
        """Crawl multiple URLs concurrently"""
        tasks = [self.fetch_page(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return dict(zip(urls, results))

# Usage example:
'''
async def main():
    async with DistributedCrawler("redis://localhost:6379/0") as crawler:
        urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net"
        ]
        results = await crawler.crawl_urls(urls)
        for url, content in results.items():
            if content:
                print(f"Successfully crawled {url}")

if __name__ == "__main__":
    asyncio.run(main())
'''