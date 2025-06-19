import streamlit as st
import os
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Streamlit secrets for Google API key   
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# Function to process PDF files and create a retriever
@st.cache_resource
def process_pdf(paths: List[str]):
    all_docs = []
    for path in paths:
        loader = PyPDFLoader(path)
        docs = loader.load()
        logger.info(f"Loaded document from {path}")
        all_docs.extend(docs)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,  # Correct parameter name
    )
    chunks = text_splitter.split_documents(all_docs)
    logger.info(f"Split documents into {len(chunks)} chunks")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-exp-03-07",
        task_type="RETRIEVAL_DOCUMENT"
    )
    vectordb = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    logger.info("Created FAISS vector store (in-memory)")
    return vectordb


# Function to search the retriever with a query
def rag_tool(query: str, vectordb) -> list:
    """
    Takes a query string and a vector store,
    performs retrieval, and returns the top 3 matching chunks.
    """
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    results = retriever.get_relevant_documents(query)
    return results