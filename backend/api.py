from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import json
from dotenv import load_dotenv

# Import our custom modules
from code_assist import generate_code, debug_code

load_dotenv()

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

app = FastAPI(title="Tengen.ai Research Assistant API", version="1.0.0")

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
    """Main chat endpoint"""
    try:
        last_message = chat_request.messages[-1]
        prompt = last_message.content
        
        # Use code generation for all queries for now
        response_text = generate_code(prompt)
        
        return StreamingResponse(stream_response(response_text), media_type="text/plain")
    except Exception as e:
        print(f"Chat error: {str(e)}")
        error_text = f"I encountered an error: {str(e)}. I'm still learning and improving!"
        return StreamingResponse(stream_response(error_text), media_type="text/plain")

@app.post("/code-assist")
async def code_assist(chat_request: ChatRequest):
    """Code assistance endpoint"""
    try:
        last_message = chat_request.messages[-1]
        prompt = last_message.content
        
        response_text = generate_code(prompt)
        
        return StreamingResponse(stream_response(response_text), media_type="text/plain")
    except Exception as e:
        print(f"Code assist error: {str(e)}")
        error_text = f"Code assistance error: {str(e)}"
        return StreamingResponse(stream_response(error_text), media_type="text/plain")

@app.post("/code/generate")
async def generate_code_endpoint(request: CodeRequest):
    """Generate code based on prompt"""
    try:
        code = generate_code(request.prompt)
        return JSONResponse({"code": code, "type": request.code_type})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/code/debug")
async def debug_code_endpoint(request: DebugRequest):
    """Debug provided code"""
    try:
        debug_result = debug_code(request.code)
        return JSONResponse({"debug_result": debug_result, "language": request.language})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload files"""
    try:
        contents = await file.read()
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save file to data directory
        file_path = os.path.join("data", file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return JSONResponse({
            "filename": file.filename, 
            "size": len(contents),
            "status": "uploaded",
            "message": "File uploaded successfully"
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        return {
            "status": "healthy",
            "google_api_configured": bool(api_key and api_key != "your_google_api_key_here")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}