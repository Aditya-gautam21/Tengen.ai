from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os
import json
from dotenv import load_dotenv

# Import our custom modules
from code_assist import generate_code, debug_code
from rag_pipeline import create_qa_chain, load_documents, split_text, create_vectorstore, query_documents
from web_scraper import scrape_research_topic

load_dotenv()

# Global variable for QA chain
qa_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global qa_chain
    try:
        # Create data and db directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("db", exist_ok=True)
        
        # Initialize QA chain if documents exist
        if os.path.exists("data") and os.listdir("data"):
            documents = load_documents()
            if documents:
                texts = split_text(documents)
                create_vectorstore(texts)
                qa_chain = create_qa_chain()
                print("QA chain initialized successfully")
        else:
            print("No documents found in data directory")
    except Exception as e:
        print(f"Error initializing QA chain: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down...")

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ResearchRequest(BaseModel):
    topic: str
    max_results: Optional[int] = 10

class CodeRequest(BaseModel):
    prompt: str
    code_type: Optional[str] = "general"

class DebugRequest(BaseModel):
    code: str
    language: Optional[str] = "python"

app = FastAPI(
    title="Tengen.ai Research Assistant API", 
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



async def stream_response(text: str):
    """Stream response character by character"""
    for char in text:
        yield char
        await asyncio.sleep(0.01)

@app.get("/")
async def root():
    return {"message": "Tengen.ai Research Assistant API", "status": "running"}

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """Main chat endpoint that handles research queries with auto-research"""
    global qa_chain
    
    try:
        last_message = chat_request.messages[-1]
        prompt = last_message.content
        
        # Check if this looks like a research query
        research_keywords = ["what is", "tell me about", "explain", "research", "find information", "learn about"]
        is_research_query = any(keyword in prompt.lower() for keyword in research_keywords)
        
        # If it's a research query and we don't have relevant data, do research first
        if is_research_query and not qa_chain:
            print(f"Auto-researching topic: {prompt}")
            # Extract topic from the prompt (simplified)
            topic = prompt.replace("what is", "").replace("tell me about", "").replace("explain", "").strip()
            
            # Do research
            scrape_result = scrape_research_topic(topic, 3)
            if scrape_result["status"] == "success":
                documents = load_documents()
                if documents:
                    texts = split_text(documents)
                    create_vectorstore(texts)
                    qa_chain = create_qa_chain()
        
        # Generate response
        if qa_chain:
            result = qa_chain({"query": prompt})
            response_text = result["result"]
        else:
            # Fallback to code generation for non-research queries
            response_text = generate_code(prompt)
        
        return StreamingResponse(stream_response(response_text), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/research")
async def research_topic(request: ResearchRequest):
    """Research a topic and provide chat-based response with sources"""
    global qa_chain
    
    try:
        # Scrape web data for the topic
        scrape_result = scrape_research_topic(request.topic, request.max_results)
        
        if scrape_result["status"] == "success":
            # Reload documents and recreate vectorstore with new data
            documents = load_documents()
            if documents:
                texts = split_text(documents)
                create_vectorstore(texts)
                qa_chain = create_qa_chain()
                
                # Generate a comprehensive response based on the research
                research_summary = "\n".join([result["content"][:500] for result in scrape_result["results"]])
                
                # Use the QA chain to generate a conversational response
                if qa_chain:
                    qa_result = qa_chain({
                        "query": f"Based on the research about {request.topic}, provide a comprehensive and conversational explanation. Here's the research data: {research_summary}"
                    })
                    chat_response = qa_result["result"]
                else:
                    chat_response = f"Based on my research about {request.topic}, here's what I found:\n\n{research_summary[:1000]}..."
            
            response = {
                "topic": request.topic,
                "status": "completed",
                "message": chat_response,
                "results_count": scrape_result["results_count"],
                "sources": [
                    {
                        "title": result["title"],
                        "url": result["url"],
                        "summary": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
                    }
                    for result in scrape_result["results"]
                ]
            }
        else:
            response = {
                "topic": request.topic,
                "status": "error",
                "message": f"I couldn't research {request.topic} right now. {scrape_result['message']}",
                "sources": []
            }
        
        return JSONResponse(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research error: {str(e)}")

@app.post("/code-assist")
async def code_assist(chat_request: ChatRequest):
    """Code assistance endpoint"""
    try:
        last_message = chat_request.messages[-1]
        prompt = last_message.content
        
        # Generate code using our code_assist module
        response_text = generate_code(prompt)
        
        return StreamingResponse(stream_response(response_text), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code assist error: {str(e)}")

@app.post("/code/generate")
async def generate_code_endpoint(request: CodeRequest):
    """Generate code based on prompt"""
    try:
        code = generate_code(request.prompt)
        return JSONResponse({"code": code, "type": request.code_type})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation error: {str(e)}")

@app.post("/code/debug")
async def debug_code_endpoint(request: DebugRequest):
    """Debug provided code"""
    try:
        debug_result = debug_code(request.code)
        return JSONResponse({"debug_result": debug_result, "language": request.language})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code debug error: {str(e)}")

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process research documents"""
    try:
        contents = await file.read()
        
        # Save file to data directory
        file_path = os.path.join("data", file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # If it's a JSON file, try to process it for the RAG pipeline
        if file.filename.endswith('.json'):
            try:
                # Reload documents and recreate vectorstore
                documents = load_documents()
                if documents:
                    texts = split_text(documents)
                    create_vectorstore(texts)
                    qa_chain = create_qa_chain()
                    
                return JSONResponse({
                    "filename": file.filename, 
                    "size": len(contents),
                    "status": "processed",
                    "message": "File uploaded and processed for research"
                })
            except Exception as e:
                return JSONResponse({
                    "filename": file.filename, 
                    "size": len(contents),
                    "status": "uploaded",
                    "message": f"File uploaded but processing failed: {str(e)}"
                })
        
        return JSONResponse({
            "filename": file.filename, 
            "size": len(contents),
            "status": "uploaded"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "qa_chain_ready": qa_chain is not None,
        "google_api_configured": bool(os.getenv("GOOGLE_API_KEY"))
    }