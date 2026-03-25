import time
import random
from urllib.parse import urlparse
from collections import defaultdict

class RateLimitedCrawler:
    def __init__(self):
        # Per-domain request tracking
        self.domain_last_request = defaultdict(float)
        self.domain_backoff = defaultdict(lambda: 1.0)
        
        # Base crawl settings
        self.min_delay = 1.0  # Minimum seconds between requests
        self.max_backoff = 60.0  # Maximum backoff in seconds
        self.backoff_factor = 2.0  # Multiplicative factor for backoff

    def get_domain(self, url):
        """Extract domain from URL"""
        return urlparse(url).netloc

    def wait_for_rate_limit(self, url):
        """Intelligent rate limiting with exponential backoff"""
        domain = self.get_domain(url)
        current_time = time.time()
        
        # Calculate wait time needed
        elapsed = current_time - self.domain_last_request[domain]
        required_delay = max(self.min_delay * self.domain_backoff[domain], self.min_delay)
        
        if elapsed < required_delay:
            sleep_time = required_delay - elapsed
            time.sleep(sleep_time + random.uniform(0, 1))

    def crawl(self, url):
        """Main crawling method with rate limiting"""
        domain = self.get_domain(url)
        
        try:
            self.wait_for_rate_limit(url)
            
            # Simulated request - replace with actual crawling logic
            success = self._make_request(url)
            
            if success:
                # Reduce backoff on success
                self.domain_backoff[domain] = max(
                    1.0,
                    self.domain_backoff[domain] / self.backoff_factor
                )
            else:
                # Increase backoff on failure
                self.domain_backoff[domain] = min(
                    self.max_backoff,
                    self.domain_backoff[domain] * self.backoff_factor
                )
            
            self.domain_last_request[domain] = time.time()
            return success
            
        except Exception as e:
            # Increase backoff on errors
            self.domain_backoff[domain] = min(
                self.max_backoff,
                self.domain_backoff[domain] * self.backoff_factor
            )
            raise e

    def _make_request(self, url):
        """Placeholder for actual request logic"""
        # TODO: Implement actual HTTP request handling
        return True

    def get_domain_stats(self):
        """Return current domain statistics"""
        stats = {}
        for domain in self.domain_last_request:
            stats[domain] = {
                'last_request': self.domain_last_request[domain],
                'current_backoff': self.domain_backoff[domain]
            }
        return stats