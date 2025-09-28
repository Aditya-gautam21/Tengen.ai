import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

DATA_PATH = "data"
DB_PATH = "db"

def load_documents() -> List[str]:
    """Load documents from JSON files in the data directory"""
    documents = []
    
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        return documents
    
    try:
        for filename in os.listdir(DATA_PATH):
            if filename.endswith('.json'):
                filepath = os.path.join(DATA_PATH, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Handle different JSON structures
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    # Try different possible content fields
                                    content = item.get('content') or item.get('text') or item.get('body') or str(item)
                                    documents.append(content)
                                else:
                                    documents.append(str(item))
                        elif isinstance(data, dict):
                            content = data.get('content') or data.get('text') or data.get('body') or str(data)
                            documents.append(content)
                        else:
                            documents.append(str(data))
                            
                except json.JSONDecodeError as e:
                    print(f"Error reading JSON file {filename}: {e}")
                except Exception as e:
                    print(f"Error processing file {filename}: {e}")
    except Exception as e:
        print(f"Error loading documents: {e}")
    
    return documents

def split_text(documents: List[str]):
    """Split documents into chunks for better retrieval"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        texts = text_splitter.create_documents(documents)
        return texts
    except Exception as e:
        print(f"Error splitting text: {e}")
        return []

def create_vectorstore(texts):
    """Create and persist vector store from text chunks"""
    try:
        if not texts:
            print("No texts to create vectorstore")
            return None
            
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # Ensure CPU usage
        )

        if not os.path.exists(DB_PATH):
            os.makedirs(DB_PATH)

        vectordb = Chroma.from_documents(
            documents=texts, 
            embedding=embeddings, 
            persist_directory=DB_PATH
        )
        vectordb.persist()
        print(f"Vector store created with {len(texts)} documents")
        return vectordb
    except Exception as e:
        print(f"Error creating vectorstore: {e}")
        return None

def create_qa_chain():
    """Create QA chain for question answering"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0.3
        )

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        if not os.path.exists(DB_PATH):
            print("Vector database not found. Please upload documents first.")
            return None
            
        vectordb = Chroma(
            persist_directory=DB_PATH, 
            embedding_function=embeddings
        )
        retriever = vectordb.as_retriever(
            search_kwargs={"k": 5}  # Return top 5 relevant documents
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=True
        )
        
        print("QA chain created successfully")
        return qa_chain
    except Exception as e:
        print(f"Error creating QA chain: {e}")
        return None

def query_documents(question: str, qa_chain=None) -> Dict[str, Any]:
    """Query the document database"""
    if not qa_chain:
        qa_chain = create_qa_chain()
    
    if not qa_chain:
        return {
            "answer": "No documents available for querying. Please upload research documents first.",
            "sources": []
        }
    
    try:
        result = qa_chain({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.page_content[:200] + "..." for doc in result.get("source_documents", [])]
        }
    except Exception as e:
        return {
            "answer": f"Error querying documents: {str(e)}",
            "sources": []
        }