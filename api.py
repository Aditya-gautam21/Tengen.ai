# api.py

import os
import time
import sys
import subprocess
from fastapi import FastAPI, HTTPException, Body
from dotenv import load_dotenv
from rag_pipeline import load_documents, split_text, create_vector_store, create_qa_chain

load_dotenv()

app = FastAPI()


# --- RAG Endpoint (no changes needed here) ---
@app.post("/ask")
async def ask_question(query: str = Body(..., embed=True)):
    """
    This endpoint takes a user's query, processes it through the RAG pipeline,
    and returns the answer.
    """
    try:
        # 1. Load the data from the 'data' directory
        documents = load_documents()
        if not documents:
            raise HTTPException(status_code=404,
                                detail="No data found. Please scrape a topic first using the /scrape endpoint.")

        # 2. Split the text
        texts = split_text(documents)

        # 3. Create the vector store
        create_vector_store(texts)

        # 4. Create the QA chain
        qa_chain = create_qa_chain()

        # 5. Get the answer
        result = qa_chain({"query": query})

        return {"answer": result["result"], "source_documents": result["source_documents"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Scraper Endpoint (Updated) ---
@app.post("/scrape")
async def scrape(topic: str = Body(..., embed=True)):
    """
    Starts a background Scrapy process to scrape a topic from Wikipedia.
    """
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required.")

    # Define the output directory and create it if it doesn't exist
    out_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(out_dir, exist_ok=True)

    # Create a unique filename for the scraped data
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(out_dir, f"output_{ts}.json")

    # This is the command to execute: scrapy crawl research -a topic="Your Topic" -o output.json
    # We run it as a module to ensure we're using the correct Scrapy installation
    command = [
        sys.executable,  # The current python interpreter
        "-m",
        "scrapy",
        "crawl",
        "research",
        "-a",
        f"topic={topic}",
        "-o",
        out_path,
    ]

    try:
        # The Scrapy project is in the 'scraper' subdirectory.
        # We need to run the command from that directory.
        project_dir = os.path.join(os.getcwd(), "scraper")

        # Popen runs the command in a new, non-blocking process
        subprocess.Popen(command, cwd=project_dir)

        return {"message": "Scraping process started successfully.", "topic": topic, "output_file": out_path}
    except Exception as e:
        # This will catch errors if the command itself is invalid, etc.
        raise HTTPException(status_code=500, detail=f"Failed to start scraper: {str(e)}")


@app.get("/about")
def about():
    return {
        "message": "An AI-powered research and coding assistant that lets you upload PDFs, scrape the web for insights, and generate new ideas. It supports summarization, contextual Q&A, code writing, and debugging—all in one privacy-first tool."
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)