from fastapi import FastAPI, Path, HTTPException
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import asyncioreactor, reactor
from scraper.scraper.spiders.research import ResearchSpider
import json

asyncioreactor.install()
app = FastAPI()
runner = CrawlerRunner(get_project_settings())

@app.post("/scrape")
async def scrape(topic: str):
    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")

    deferred = runner.crawl(ResearchSpider, topic=topic)
    deferred.addCallbaxk(lambda _: reactor.stop())

    reactor.run()

    try:
        with open('output.json', 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Scraping failed: {str(e)}')

@app.get("/about")
def about():
    return {'message':'An AI-powered research and coding assistant that lets you upload PDFs, scrape the web for insights, and generate new ideas. It supports summarization, contextual Q&A, code writing, and debugging—all in one privacy-first tool.'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)