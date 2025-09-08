from langchain_google_genai import ChatGoogleGenerativeAI

def generate_code(prompt: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    result = llm.invoke(f"Generate code for the following prompt: {prompt}")
    return result.content

def debug_code(code: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    result = llm.invoke(f"Debug the following code: \n\n```\n{code}\n```")
    return result.content
