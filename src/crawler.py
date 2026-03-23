import time
import random
from urllib.parse import urlparse
from collections import defaultdict

class RateLimitedCrawler:
    def __init__(self):
        self.domain_timestamps = defaultdict(list)
        self.min_delay = 1.0  # Minimum delay between requests to same domain
        self.max_delay = 30.0 # Maximum backoff delay
        self.backoff_factor = 2.0

    def get_domain(self, url):
        """Extract domain from URL"""
        return urlparse(url).netloc

    def calculate_delay(self, domain):
        """Calculate adaptive delay based on recent request history"""
        recent_requests = self.domain_timestamps[domain]
        # Clean old timestamps
        current_time = time.time()
        recent_requests = [t for t in recent_requests if current_time - t < 60]
        self.domain_timestamps[domain] = recent_requests

        if not recent_requests:
            return self.min_delay

        # Calculate request rate
        request_rate = len(recent_requests) / 60.0
        
        if request_rate > 10:  # More than 10 requests per minute
            delay = min(self.max_delay, self.min_delay * (self.backoff_factor ** (request_rate - 10)))
        else:
            delay = self.min_delay

        # Add random jitter
        delay *= (1 + random.uniform(-0.1, 0.1))
        return delay

    async def crawl(self, url):
        """Crawl URL with intelligent rate limiting"""
        domain = self.get_domain(url)
        delay = self.calculate_delay(domain)
        
        # Wait for calculated delay
        await asyncio.sleep(delay)

        try:
            # Record timestamp of request
            self.domain_timestamps[domain].append(time.time())

            # Perform actual request here
            # TODO: Implement actual crawling logic
            pass

        except Exception as e:
            # Increase backoff on errors
            self.min_delay = min(self.max_delay, self.min_delay * self.backoff_factor)
            raise

    def reset_backoff(self, domain):
        """Reset backoff settings for domain"""
        self.domain_timestamps[domain].clear()
        self.min_delay = 1.0

    async def bulk_crawl(self, urls):
        """Crawl multiple URLs with rate limiting"""
        tasks = [self.crawl(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
