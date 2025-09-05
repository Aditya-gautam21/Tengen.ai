import os, json, uuid, typing as t
from fastapi import FastAPI, HTTPException, APIRouter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import chroma
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceHub

DATA_PATH = "data"
DB_PATH = "db"

