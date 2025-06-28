import streamlit as st
import os
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Streamlit secrets for Google API key   
# os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# Function to process PDF files and create a retriever

@st.cache_resource
def process_pdf(paths: List[str]) -> str:
    all_text = []
    logger.info(f"Starting PDF processing for {len(paths)} file(s)")

    for path in paths:
        logger.info(f"Attempting to load document from {path}")
        try:
            loader = PyPDFLoader(path)
            docs = loader.load()
            logger.info(f"Successfully loaded {len(docs)} page(s) from {path}")

            for doc in docs:
                all_text.append(doc.page_content)
                
        except Exception as e:
            logger.error(f"Error loading {path}: {str(e)}")
            continue

    combined_text = "\n\n".join(all_text)
    logger.info(f"Extracted text from {len(all_text)} page(s) in total")
    logger.info(f"Extracted text is: {combined_text[:100]}")
    return combined_text


# Function to search the retriever with a query
def rag_tool(query: str, vectordb) -> list:
    """
    Takes a query string and a vector store,
    performs retrieval, and returns the top 3 matching chunks.
    """
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    results = retriever.get_relevant_documents(query)
    return results