import argparse
import sys
from pathlib import Path

# Ensure the src directory is in the Python path
# This allows importing modules from src when running main.py from the project root
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src import config # This will load .env and check for OPENAI_API_KEY
from src.data_processor import load_documents_from_directory, split_documents_into_chunks
from src.vector_store import create_and_save_vector_store, get_embedding_model, load_vector_store
from src.rag_pipeline import RAGPipeline

def build_vector_store():
    """
    Loads data, processes it, and builds/saves the vector store.
    """
    print("Starting to build vector store...")
    
    # 1. Load documents
    print(f"Loading documents from: {config.DATA_PATH}")
    raw_documents = load_documents_from_directory(config.DATA_PATH)
    if not raw_documents:
        print("No documents found. Aborting vector store build.")
        return

    # 2. Split documents into chunks
    print("Splitting documents into chunks...")
    chunks = split_documents_into_chunks(raw_documents, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    if not chunks:
        print("No chunks created. Aborting vector store build.")
        return

    # 3. Initialize embedding model
    print("Initializing embedding model...")
    embeddings = get_embedding_model()

    # 4. Create and save vector store
    print("Creating and saving vector store...")
    vector_store = create_and_save_vector_store(chunks, embeddings, str(config.VECTOR_STORE_PATH))
    
    if vector_store:
        print("Vector store built and saved successfully!")
    else:
        print("Failed to build vector store.")

def query_cli():
    """
    Starts a command-line interface to query the RAG pipeline.
    """
    print("Starting RAG Query CLI...")
    try:
        rag_system = RAGPipeline()
    except RuntimeError as e:
        print(f"Error initializing RAG Pipeline: {e}")
        print("Please ensure the vector store is built first. Run: python main.py build")
        return
    
    print("RAG system ready. Type 'exit' or 'quit' to stop.")
    while True:
        user_query = input("\nEnter your question: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        if not user_query.strip():
            continue
        
        response = rag_system.ask(user_query)
        print("\nAnswer:")
        print(response.get("answer", "No answer provided."))
        
        source_docs = response.get("source_documents", [])
        if source_docs:
            print("\nSources:")
            for i, doc in enumerate(source_docs):
                source_name = doc.metadata.get('source', 'Unknown source')
                page_number = doc.metadata.get('page', None)
                source_info = f"{source_name}"
                if page_number:
                    source_info += f" (Page {page_number})"
                print(f"  [{i+1}] {source_info}")
                # print(f"      Content snippet: {doc.page_content[:100]}...") # Optional: show snippet
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="RAG Demo Project CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the vector store from documents in data/")
    build_parser.set_defaults(func=build_vector_store)

    # Query command
    query_parser = subparsers.add_parser("query", help="Start a CLI to query the RAG pipeline")
    query_parser.set_defaults(func=query_cli)
    
    # API command (optional, if you want to run API from here too)
    # api_parser = subparsers.add_parser("api", help="Run the FastAPI application")
    # api_parser.set_defaults(func=lambda: uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True))
    # if you add this, you'll need: import uvicorn

    args = parser.parse_args()

    if args.command:
        args.func()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()