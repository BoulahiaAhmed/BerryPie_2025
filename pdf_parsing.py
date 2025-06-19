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
    for path in paths:
        try:
            loader = PyPDFLoader(path)
            docs = loader.load()
            logger.info(f"Loaded document from {path}")
            
            # Extract text from each Document object
            for doc in docs:
                all_text.append(doc.page_content)  # Access the page_content attribute
                
        except Exception as e:
            logger.error(f"Error loading {path}: {str(e)}")
            continue
    
    # Combine all text with double newlines between pages
    combined_text = "\n\n".join(all_text)  # Now joining strings, not Documents
    logger.info(f"Extracted {len(all_text)} pages of text")
    return combined_text

    # # 2. Split documents
    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=1500,
    #     chunk_overlap=200,
    #     separators=["\n\n", "\n", " ", ""]  # Better handling for PDFs
    # )
    # chunks = text_splitter.split_documents(all_docs)
    # logger.info(f"Split into {len(chunks)} chunks")

    # # 3. Initialize Embeddings (HuggingFace)
    # model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight & effective
    # embeddings = HuggingFaceEmbeddings(
    #     model_name=model_name,
    #     model_kwargs={'device': 'cpu'},  # Force CPU for Streamlit
    #     encode_kwargs={'normalize_embeddings': True}  # Better for similarity
    # )

    # # 4. Create FAISS index
    # vectordb = FAISS.from_documents(
    #     documents=chunks,
    #     embedding=embeddings
    # )
    # logger.info("Created FAISS vector store")
    # # Save
    # vectordb.save_local("faiss_index")
    # return vectordb


# Function to search the retriever with a query
def rag_tool(query: str, vectordb) -> list:
    """
    Takes a query string and a vector store,
    performs retrieval, and returns the top 3 matching chunks.
    """
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    results = retriever.get_relevant_documents(query)
    return results