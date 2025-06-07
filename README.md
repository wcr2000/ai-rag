# Project RAG base (หรือ Project RAG Demo)

## Project Overview
This project implements a basic Retrieval Augmented Generation (RAG) system. It can answer questions based on a provided set of documents by:
1.  Processing and indexing these documents into a vector store.
2.  When a query is received, retrieving relevant document chunks from the vector store.
3.  Feeding these chunks as context, along with the original query, to a Large Language Model (LLM) to generate an answer.

This demonstrates a fundamental data pipeline for RAG (data ingestion, chunking, embedding) and the application of ML models (embedding model, LLM).

## Features
*   **Document Loading:** Supports loading `.txt` and `.pdf` files from a specified directory.
*   **Document Chunking:** Splits documents into smaller, manageable chunks for efficient processing.
*   **Text Embedding Generation:** Uses OpenAI's embedding models (e.g., `text-embedding-ada-002`) to convert text chunks into vector representations. (Can be adapted for local Sentence-Transformers).
*   **Vector Store Creation & Querying:** Utilizes FAISS (a local vector store) to store and efficiently search for relevant document chunks based on query similarity.
*   **LLM Integration:** Integrates with OpenAI's GPT models (e.g., `gpt-3.5-turbo`) for answer generation based on retrieved context.
*   **Command-Line Interface:** Provides a CLI to build the vector store and ask questions.
*   **(Optional) Simple API Endpoint:** Includes a FastAPI endpoint (`/ask`) for programmatic interaction (if `src/api.py` is run).

## Technologies Used
*   **Python 3.9+**
*   **Langchain:** Framework for developing applications powered by language models.
*   **OpenAI API:** For text embeddings (e.g., `text-embedding-ada-002`) and LLM (e.g., `gpt-3.5-turbo`).
    *   *(Alternatively, `sentence-transformers` for local embeddings and Hugging Face models for local LLMs could be integrated).*
*   **FAISS (`faiss-cpu`):** For creating and managing a local vector store.
    *   *(Alternatively, `ChromaDB` could be used).*
*   **`pypdf`:** For parsing PDF documents.
*   **`python-dotenv`:** For managing environment variables.
*   **FastAPI & Uvicorn (Optional):** For creating and serving the API endpoint.
*   **`tiktoken`**: For token counting, often a dependency for OpenAI models.

## Setup Instructions

1.  **Clone the repository (if applicable) or create the project structure.**

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your OpenAI API key:
        ```
        OPENAI_API_KEY="INPUT_OPENAPI_KEY"
        ```

5.  **Add documents:**
    Place your `.txt` or `.pdf` documents into the `data/` directory. A `sample_document.txt` is provided.

## How to Run

### 1. Build the Vector Store
This step processes the documents in the `data/` directory, creates embeddings, and saves them into a local FAISS vector store located at `vector_store_index/faiss_index`.
**You must run this step first before querying.**

```bash
python main.py build
```

### 2. Query using the Command-Line Interface (CLI)
Once the vector store is built, you can ask questions:
```bash
python main.py query
```

### 3. (Optional) Run the FastAPI Application
To run the API for programmatic access:
```bash
uvicorn src.api:app --reload
```
The API will be available at `http://127.0.0.1:8000`. Access interactive documentation at `http://127.0.0.1:8000/docs`.

## Connecting to Interview Questions (Example)
*   "Give me a room type"
*   "Give me a food menu for me to day i want to eat like a pizza"