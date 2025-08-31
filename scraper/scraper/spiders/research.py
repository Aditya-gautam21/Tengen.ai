import scrapy


class ResearchSpider(scrapy.Spider):
    name = "research"
    allowed_domains = ["apple.com"]
    start_urls = []

    def __init__(self, topic='', *args, **kwargs):
        super(ResearchSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.apple.com/{topic.replace(" ","-")}/']

    def parse(self, response, **kwargs):
        paragraphs = response.css('p::text').getall()[:5]
        yield{
            'topic':response.url.split('/')[-1].replace('_',' '),
            'content': ' '.join(paragraphs).strip(),
            'source': response.url
        }
