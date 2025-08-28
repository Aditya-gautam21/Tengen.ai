from fastapi import FastAPI, Path, HTTPException

app = FastAPI()

@app.get("/about")
def about():
    return {'message':'An AI-powered research and coding assistant that lets you upload PDFs, scrape the web for insights, and generate new ideas. It supports summarization, contextual Q&A, code writing, and debugging—all in one privacy-first tool.'}