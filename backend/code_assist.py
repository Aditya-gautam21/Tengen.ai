import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():
    """Get configured LLM instance"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=api_key,
        temperature=0.7
    )

def generate_code(prompt: str) -> str:
    """Generate code based on the given prompt"""
    try:
        llm = get_llm()
        # Determine if this is a coding request
        is_code_request = any(keyword in prompt.lower() for keyword in 
                            ['code', 'function', 'program', 'script', 'debug', 'algorithm', 'class', 'method'])
        
        if is_code_request:
            enhanced_prompt = f"You are an expert programmer. Generate clean, concise code for: {prompt}. Keep response under 300 words."
        else:
            enhanced_prompt = f"You are a helpful assistant. Provide a clear, concise answer for: {prompt}. Keep response under 200 words."
        
        result = llm.invoke(enhanced_prompt)
        return result.content
    except Exception as e:
        return f"Error generating code: {str(e)}"

def debug_code(code: str) -> str:
    """Debug the provided code and suggest fixes"""
    try:
        llm = get_llm()
        debug_prompt = f"""
        You are an expert code debugger. Analyze the following code and provide:
        
        1. Identify any bugs or issues
        2. Suggest fixes with explanations
        3. Recommend improvements
        4. Provide the corrected code if needed
        
        Code to debug:
        ```
        {code}
        ```
        """
        
        result = llm.invoke(debug_prompt)
        return result.content
    except Exception as e:
        return f"Error debugging code: {str(e)}"
