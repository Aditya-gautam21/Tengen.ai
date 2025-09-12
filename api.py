from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Literal
from fastapi.middleware.cors import CORSMiddleware
import asyncio

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def your_model_logic(prompt: str):
    response_text = f"This is a streamed response to your prompt: '{prompt}'"
    for char in response_text:
        yield char
        await asyncio.sleep(0.02)

@app.post("/code-assist")
async def code_assist(chat_request: ChatRequest):
    last_message = chat_request.messages[-1]
    prompt = last_message.content
    return StreamingResponse(your_model_logic(prompt), media_type="text/plain")