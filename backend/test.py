import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

# List models
for m in genai.list_models():
    if "gemini" in m.name:
        print(m.name, "—", m.supported_generation_methods)
