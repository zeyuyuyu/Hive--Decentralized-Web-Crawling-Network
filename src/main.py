import asyncio
import aiohttp
import hashlib
import json
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)

class DistributedTaskScheduler:
    def __init__(self, workers: List[str], task_queue: asyncio.Queue):
        self.workers = workers
        self.task_queue = task_queue
        self.worker_loads = {worker: 0 for worker in workers}

    async def schedule_tasks(self):
        while True:
            if self.task_queue.empty():
                await asyncio.sleep(1)
                continue

            task = await self.task_queue.get()
            least_loaded_worker = min(self.worker_loads, key=self.worker_loads.get)
            self.worker_loads[least_loaded_worker] += 1

            async with aiohttp.ClientSession() as session:
                async with session.post(f'http://{least_loaded_worker}/process_task', json=task) as resp:
                    if resp.status == 200:
                        logging.info(f'Task processed by {least_loaded_worker}')
                    else:
                        logging.error(f'Error processing task on {least_loaded_worker}')
                    self.worker_loads[least_loaded_worker] -= 1

class HiveWebCrawler:
    def __init__(self, workers: List[str], seed_urls: List[str]):
        self.task_queue = asyncio.Queue()
        self.scheduler = DistributedTaskScheduler(workers, self.task_queue)
        self.seed_urls = seed_urls

    async def crawl(self):
        for url in self.seed_urls:
            await self.task_queue.put({'url': url})

        await self.scheduler.schedule_tasks()

async def main():
    workers = ['worker1:8000', 'worker2:8000', 'worker3:8000']
    seed_urls = ['https://example.com', 'https://hive.org', 'https://decentralizedweb.net']

    crawler = HiveWebCrawler(workers, seed_urls)
    await crawler.crawl()

if __name__ == '__main__':
    asyncio.run(main())