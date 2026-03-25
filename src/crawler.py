import time
import random
from collections import defaultdict
from datetime import datetime, timedelta

class DistributedCrawler:
    def __init__(self):
        # Track requests per domain
        self.domain_requests = defaultdict(list)
        # Default politeness settings
        self.min_delay = 1.0  # seconds between requests
        self.max_requests_per_domain = 60  # per minute
        self.respect_robots_txt = True
        
    def get_domain_from_url(self, url):
        """Extract domain from URL"""
        # Basic domain extraction - could be enhanced
        return url.split('/')[2]
    
    def can_crawl_url(self, url):
        """Check if we can crawl URL based on politeness policies"""
        domain = self.get_domain_from_url(url)
        now = datetime.now()
        
        # Clean old requests
        self.domain_requests[domain] = [
            req_time for req_time in self.domain_requests[domain]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check request count
        if len(self.domain_requests[domain]) >= self.max_requests_per_domain:
            return False
            
        # Check delay since last request
        if self.domain_requests[domain]:
            last_req = max(self.domain_requests[domain])
            if (now - last_req).total_seconds() < self.min_delay:
                return False
                
        return True
    
    def crawl_url(self, url):
        """Crawl a URL with politeness policies"""
        if not self.can_crawl_url(url):
            return None
            
        domain = self.get_domain_from_url(url)
        
        try:
            # Record request time
            self.domain_requests[domain].append(datetime.now())
            
            # Add jitter to delays
            jitter = random.uniform(0, 0.5)
            time.sleep(self.min_delay + jitter)
            
            # TODO: Actual crawling logic here
            # This is where you'd make the HTTP request
            # and process the response
            
            return {'url': url, 'status': 'success'}
            
        except Exception as e:
            return {'url': url, 'status': 'error', 'error': str(e)}
    
    def set_politeness_policy(self, min_delay=None, max_requests=None, respect_robots=None):
        """Configure crawler politeness settings"""
        if min_delay is not None:
            self.min_delay = float(min_delay)
        if max_requests is not None:
            self.max_requests_per_domain = int(max_requests)
        if respect_robots is not None:
            self.respect_robots_txt = bool(respect_robots)
            
    def __str__(self):
        return f'DistributedCrawler(delay={self.min_delay}s, max_requests={self.max_requests_per_domain}/min)'
