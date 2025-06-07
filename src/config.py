import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent # project-rag-demo directory
DATA_PATH = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "vector_store_index"
VECTOR_STORE_PATH = VECTOR_STORE_DIR / "faiss_index" # For FAISS

# Models
EMBEDDING_MODEL_NAME = "text-embedding-ada-002" # OpenAI embedding model
# Or for local embeddings with Sentence Transformers:
# EMBEDDING_MODEL_NAME_LOCAL = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "gpt-3.5-turbo"

# Data Processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Vector Store
K_RETRIEVED_DOCS = 3 # Number of relevant documents to retrieve

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")

# Create vector store directory if it doesn't exist
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)