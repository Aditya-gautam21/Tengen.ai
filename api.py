from scrapy.utils.reactor import install_reactor  # safe stdlib import
install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

from fastapi import FastAPI, HTTPException
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from crochet import setup, run_in_reactor
from scraper.scraper.spiders.research import ResearchSpider
import logging, os, json, time
from rag_pipeline import load_documents, split_text, create_vectorstore, create_qa_chain
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
setup()

app = FastAPI()

@run_in_reactor
def run_spider(topic: str):
    settings = get_project_settings()

    # Absolute output folder
    out_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(out_dir, exist_ok=True)
    # Unique file per run to avoid races
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(out_dir, f"output_{ts}.json")

    # Configure feeds programmatically
    settings.set(
        "FEEDS",
        {out_path: {"format": "json", "overwrite": True}},
        priority="project",
    )

    configure_logging()
    runner = CrawlerRunner(settings)
    d = runner.crawl(ResearchSpider, topic=topic)

    # When crawl finishes, return the path to read
    def _return_path(_):
        return out_path

    d.addCallback(_return_path)
    return d  # Crochet wraps Deferred; .wait() used in route

@app.post("/scrape")
async def scrape(topic: str):
    logger.debug(f"Received topic: {topic}")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")
    try:
        out_path = run_spider(topic).wait(timeout=60.0)
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug("Scraping completed successfully")
        return data
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/about")
def about():
    return {
        "message": "An AI-powered research and coding assistant that lets you upload PDFs, scrape the web for insights, and generate new ideas. It supports summarization, contextual Q&A, code writing, and debugging—all in one privacy-first tool."
    }

@app.post("/ask")
async def ask_question(query: str):
    #1. Load documents
    documents = load_documents()
    if not documents:
        raise HTTPException(status_code=404, detail="No data found")

    #2. Split the text into chunks
    texts = split_text(documents)

    #3. Create the vectorstore for the embeddings
    create_vectorstore(texts)

    #4. Create the QA chain
    qa_chain = create_qa_chain()

    #5. Get the answer
    result = qa_chain({"query": query})

    return {"answer": result["result"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
