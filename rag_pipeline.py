import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings # Updated import
from langchain_community.vectorstores import Chroma # Updated import
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
import json

DATA_PATH = "data"
DB_PATH = "db"

def load_documents():
    documents = []

    for filename in os.listdir(DATA_PATH):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_PATH, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    documents.append(item['content'])

    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.create_documents(documents)
    return texts

def create_vectorstore(texts):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=DB_PATH)
    vectordb.persist()
    return vectordb

def create_qa_chain():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-latest")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = vectordb.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type="stuff",
                                           retriever=retriever,
                                           return_source_docuents=True)
    return qa_chain