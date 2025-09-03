from typing import List, Dict, Any

class CollectPipeline:
    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def open_spider(self, spider):
        self.items.clear()

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        spider.crawled_items = self.items  # attach results to spider for retrieval
