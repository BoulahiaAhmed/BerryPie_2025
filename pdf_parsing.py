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
    """Process multiple PDF files and extract text content with detailed logging.
    
    Args:
        paths: List of file paths to PDF documents
        
    Returns:
        Combined text from all PDFs separated by double newlines
    """
    logger.info(f"Starting PDF processing for {len(paths)} files: {paths}")
    all_text = []
    total_pages = 0
    processed_files = 0
    
    for path in paths:
        try:
            logger.debug(f"Opening PDF: {path}")
            with open(path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                num_pages = len(reader.pages)
                logger.info(f"Processing PDF: {path} - {num_pages} pages")
                
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            all_text.append(page_text)
                            total_pages += 1
                        else:
                            logger.warning(f"Empty page #{page_num} in {path}")
                    except Exception as page_e:
                        logger.error(f"Error processing page #{page_num} in {path}: {str(page_e)}")
                
                processed_files += 1
                logger.debug(f"Completed processing: {path}")

        except Exception as e:
            logger.error(f"Critical error processing {path}: {str(e)}")
            logger.exception("Exception details:")  # Log full traceback
            continue
    
    # Combine all text with double newlines between pages
    combined_text = "\n\n".join(all_text)
    
    # Log summary metrics
    logger.info(
        f"PDF processing complete. "
        f"Files: {processed_files}/{len(paths)} succeeded, "
        f"Pages: {total_pages}, "
        f"Total characters: {len(combined_text)}"
    )
    
    if not combined_text:
        logger.warning("No text extracted from any PDF files!")
    
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