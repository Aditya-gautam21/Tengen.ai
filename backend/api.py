from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import json
import re
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
import logging

# Import our custom modules
from code_assist import generate_code, debug_code

load_dotenv()
logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ResearchRequest(BaseModel):
    topic: str
    max_results: Optional[int] = Field(default=10, ge=1, le=50)
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Topic must be at least 2 characters long')
        # Sanitize input
        return re.sub(r'[<>"\']', '', v.strip())

class CodeRequest(BaseModel):
    prompt: str
    code_type: Optional[str] = Field(default="general", regex=r'^[a-zA-Z0-9_-]+$')
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Prompt must be at least 5 characters long')
        return v.strip()[:2000]  # Limit length

class DebugRequest(BaseModel):
    code: str
    language: Optional[str] = Field(default="python", regex=r'^[a-zA-Z0-9_+-]+$')
    
    @validator('code')
    def validate_code(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Code cannot be empty')
        return v.strip()[:10000]  # Limit length

app = FastAPI(title="Tengen.ai Research Assistant API", version="1.0.0")

# Secure CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
origins = [origin.strip() for origin in allowed_origins if origin.strip()]

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

# Allowed file types and size limits
ALLOWED_EXTENSIONS = {'.json', '.txt', '.csv', '.md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    if not file.filename:
        return False
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Validate filename (no path traversal)
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        return False
    
    return True

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload files with security validation"""
    try:
        # Validate file
        if not validate_file(file):
            raise HTTPException(status_code=400, detail="Invalid file type or name")
        
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Create secure data directory
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Generate safe filename
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        file_path = data_dir / safe_filename
        
        # Ensure file path is within data directory
        if not str(file_path.resolve()).startswith(str(data_dir.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Save file securely
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"File uploaded: {safe_filename}, size: {len(contents)}")
        
        return JSONResponse({
            "filename": safe_filename, 
            "size": len(contents),
            "status": "uploaded",
            "message": "File uploaded successfully"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")

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