from typing import List
from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings # For local embeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document as LangchainDocument

from . import config

def get_embedding_model():
    """
    Initializes and returns the embedding model.
    """
    # Using OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL_NAME,
        openai_api_key=config.OPENAI_API_KEY
    )
    # Example for local Sentence Transformer embeddings (uncomment if you want to use this)
    # embeddings = HuggingFaceEmbeddings(
    #     model_name=config.EMBEDDING_MODEL_NAME_LOCAL,
    #     model_kwargs={'device': 'cpu'} # Or 'cuda' if GPU is available
    # )
    return embeddings

def create_and_save_vector_store(
    chunks: List[LangchainDocument],
    embeddings_model, # Pass the initialized model
    index_path: str = str(config.VECTOR_STORE_PATH)
):
    """
    Creates a FAISS vector store from document chunks and saves it locally.
    """
    if not chunks:
        print("No chunks provided to create vector store.")
        return None
        
    print(f"Creating vector store with {len(chunks)} chunks...")
    try:
        vector_store = FAISS.from_documents(documents=chunks, embedding=embeddings_model)
        vector_store.save_local(index_path)
        print(f"Vector store saved to {index_path}")
        return vector_store
    except Exception as e:
        print(f"Error creating or saving vector store: {e}")
        return None


def load_vector_store(
    index_path: str = str(config.VECTOR_STORE_PATH),
    embeddings_model=None # Pass the initialized model
):
    """
    Loads an existing FAISS vector store from local storage.
    """
    if embeddings_model is None:
        embeddings_model = get_embedding_model()
        
    if not config.VECTOR_STORE_PATH.exists():
        print(f"Vector store not found at {index_path}. Please create it first.")
        return None
    try:
        print(f"Loading vector store from {index_path}...")
        # allow_dangerous_deserialization=True is needed for FAISS with custom Python objects if not using default pickle
        vector_store = FAISS.load_local(
            index_path, 
            embeddings_model, 
            allow_dangerous_deserialization=True # Important for FAISS
        )
        print("Vector store loaded successfully.")
        return vector_store
    except Exception as e:
        print(f"Error loading vector store: {e}")
        # Consider if the index is corrupted or incompatible embedding model
        return None


def search_vector_store(vector_store: FAISS, query: str, k: int = config.K_RETRIEVED_DOCS) -> List[LangchainDocument]:
    """
    Searches the vector store for documents similar to the query.
    """
    if vector_store is None:
        print("Vector store is not loaded. Cannot perform search.")
        return []
    print(f"Searching for top {k} relevant documents for query: '{query}'")
    retrieved_docs = vector_store.similarity_search(query, k=k)
    print(f"Retrieved {len(retrieved_docs)} documents.")
    return retrieved_docs

if __name__ == '__main__':
    # This part is for testing and assumes documents are processed and chunked.
    # For a full flow, you'd call data_processor first.
    
    # Dummy chunks for testing if run directly
    from .data_processor import load_documents_from_directory, split_documents_into_chunks
    print("Testing vector_store.py...")

    # 1. Initialize embeddings model
    embeddings = get_embedding_model()

    # 2. Load and split documents (simulating a build process)
    raw_docs = load_documents_from_directory(config.DATA_PATH)
    if raw_docs:
        doc_chunks = split_documents_into_chunks(raw_docs)
        
        # 3. Create and save vector store
        print("\nAttempting to create and save vector store...")
        vs = create_and_save_vector_store(doc_chunks, embeddings)
        
        if vs:
            print("Vector store created successfully.")
        else:
            print("Failed to create vector store. Exiting test.")
            exit()

        # 4. Load the vector store
        print("\nAttempting to load vector store...")
        loaded_vs = load_vector_store(embeddings_model=embeddings) # Pass model for consistency
        
        if loaded_vs:
            # 5. Search the vector store
            test_query = "What is RAG?"
            print(f"\nSearching for: '{test_query}'")
            results = search_vector_store(loaded_vs, test_query, k=2)
            if results:
                for i, doc in enumerate(results):
                    print(f"\nResult {i+1}:")
                    print(f"Content: {doc.page_content[:200]}...")
                    print(f"Source: {doc.metadata.get('source', 'N/A')}")
            else:
                print("No results found.")
        else:
            print("Failed to load vector store for searching.")
    else:
        print("No documents found to process for vector store testing.")