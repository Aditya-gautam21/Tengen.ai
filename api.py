import os, time, sys, subprocess
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware
from dotenv import load_dotenv
import json
from rag_pipeline import load_documents, split_text, create_vectorstore, create_qa_chain
from code_assist import generate_code, debug_code

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/about")
def about():
    return {
        "message": "An AI-powered research and coding assistant that lets you upload PDFs, scrape the web for insights, and generate new ideas. It supports summarization, contextual Q&A, code writing, and debugging—all in one privacy-first tool."
    }

@app.post("/ask")
async def ask_question(query: str = Body(..., embed=True)):
    """
    This endpoint takes a user's query, processes it through the RAG pipeline,
    and returns the answer.
    """
    try:
        documents = load_documents()
        if not documents:
            raise HTTPException(status_code=404,
                                detail="No data found. Please scrape a topic first using the /scrape endpoint.")
        texts = split_text(documents)
        create_vectorstore(texts)
        qa_chain = create_qa_chain()
        result = qa_chain({"query": query})
        return {"answer": result["result"], "source_documents": result["source_documents"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape")
async def scrape(topic: str = Body(..., embed=True)):
    """
    Starts a Scrapy process to scrape a topic from Wikipedia, waits for it to complete,
    and returns the scraped data.
    """
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required.")

    out_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(out_dir, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(out_dir, f"output_{ts}.json")

    command = [
        sys.executable,
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
        project_dir = os.path.join(os.getcwd(), "scraper")

        result = subprocess.run(command, cwd=project_dir, check=True, capture_output=True, text=True)

        if not os.path.exists(out_path):
            raise HTTPException(status_code=500, detail=f"Scraper failed to create output file. Error: {result.stderr}")

        with open(out_path, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)

        return scraped_data

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Scraper process failed: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start or process scraper: {str(e)}")


@app.post("/code-assist")
async def code_assist_endpoint(prompt: str = Body(...), code: str = Body(None), mode: str = Body("generate")):
    """
    Provides code generation and debugging assistance.
    - mode='generate': Generates code based on the prompt.
    - mode='debug': Debugs the provided code.
    """
    if mode == "generate":
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required for code generation.")
        response = generate_code(prompt)
        return {"response": response}
    elif mode == "debug":
        if not code:
            raise HTTPException(status_code=400, detail="Code is required for debugging.")
        response = debug_code(code)
        return {"response": response}
    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Choose 'generate' or 'debug'.")

@app.post("/chat")
async def chat(payload: dict):
    """
    Unified chat endpoint.
    Decides between research Q&A, scraping, and code assistance.
    """
    try:
        user_message = payload.get("message", "").lower()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required.")

        # 🔹 Handle code generation / debugging
        if "debug" in user_message:
            code = payload.get("code", "")
            if not code:
                raise HTTPException(status_code=400, detail="Code is required for debugging.")
            response = debug_code(code)
            return {"response": response}

        elif "code" in user_message or "generate" in user_message:
            response = generate_code(user_message)
            return {"response": response}

        # 🔹 Handle scraping explicitly
        elif "scrape" in user_message or "research" in user_message:
            topic = user_message.replace("scrape", "").replace("research", "").strip()
            if not topic:
                raise HTTPException(status_code=400, detail="Please specify a topic to scrape.")
            scraped_data = await scrape(topic)
            return {"response": f"Here’s what I found on {topic}:", "data": scraped_data}

        # 🔹 Otherwise use RAG pipeline for Q&A
        else:
            documents = load_documents()
            if not documents:
                return {"response": "No data found. Please scrape a topic first using the /scrape endpoint."}

            texts = split_text(documents)
            create_vectorstore(texts)
            qa_chain = create_qa_chain()
            result = qa_chain({"query": user_message})
            return {
                "response": result["result"],
                "source_documents": result["source_documents"],
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)