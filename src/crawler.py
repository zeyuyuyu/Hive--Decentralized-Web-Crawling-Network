import multiprocessing as mp
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from collections import deque

class DistributedCrawler:
    def __init__(self, seed_urls, num_workers):
        self.seed_urls = seed_urls
        self.num_workers = num_workers
        self.url_queue = deque(seed_urls)
        self.visited_urls = set()
        self.results = mp.Queue()

    def crawl(self):
        processes = []
        for _ in range(self.num_workers):
            p = mp.Process(target=self.worker)
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        return self.collect_results()

    def worker(self):
        while True:
            try:
                url = self.url_queue.popleft()
            except IndexError:
                return

            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                self.results.put((url, soup.get_text()))
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href and self.is_valid_url(href):
                        self.url_queue.append(href)
            except:
                pass

    def collect_results(self):
        results = []
        while not self.results.empty():
            results.append(self.results.get())
        return results

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
