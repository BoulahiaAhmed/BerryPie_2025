import streamlit as st
import os
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma  # or Pinecone, Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Set up Streamlit secrets for Google API key   
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]


# Function to process PDF files and create a retriever
@st.cache_resource
def process_pdf(path):
    docs = UnstructuredPDFLoader(path).load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=1500, overlap=200).split_documents(docs)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-exp-03-07",
        task_type="RETRIEVAL_DOCUMENT"
    )
    vectordb = Chroma.from_documents(chunks, embeddings)
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