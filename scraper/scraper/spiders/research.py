import scrapy
import re

class ResearchSpider(scrapy.Spider):
    name = "research"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = []
    handle_httpstatus_list = [404]

    def __init__(self, topic='', *args, **kwargs):
        super(ResearchSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://en.wikipedia.org/wiki/{topic.replace(" ", "_")}']

    def parse(self, response):
        if response.status == 404:
            self.logger.error(f"Page not found: {response.url}")
            yield {'error': 'Page not found', 'test': 'This should appear'}
            return

        paragraph_elements = response.xpath('//p')[:5]
        paragraphs = []
        for p in paragraph_elements:
            full_text = p.xpath('string(.)').get()
            cleaned_text = re.sub(r'\s+', ' ', full_text).strip()
            if cleaned_text:
                paragraphs.append(cleaned_text)

        if not paragraphs:
            self.logger.warning("No paragraphs found")
            yield {'test': 'No data - fallback item'}
        else:
            yield {
                'topic': response.url.split('/wiki/')[-1].replace('_', ' '),
                'content': ' '.join(paragraphs),
                'source': response.url
            }
