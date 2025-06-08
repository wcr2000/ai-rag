# Project RAG base

## Project Overview
This project implements a basic Retrieval Augmented Generation (RAG) system. It can answer questions based on a provided set of documents by:
1.  Processing and indexing these documents into a vector store.
2.  When a query is received, retrieving relevant document chunks from the vector store.
3.  Feeding these chunks as context, along with the original query, to a Large Language Model (LLM) to generate an answer.

This demonstrates a fundamental data pipeline for RAG (data ingestion, chunking, embedding) and the application of ML models (embedding model, LLM).

## Features
*   **Document Loading:** Supports loading `.txt` and `.pdf`, `.json` files from a specified directory.
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
    Place your `.txt` or `.pdf`, `.json` documents into the `data/` directory. A `sample_document.txt` is provided.

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

Docker build
```bash
docker build -t project-rag-api .
```

## Connecting to Interview Questions (Example)
*   "Give me a room type"
*   "Give me a food menu for me to day i want to eat like a pizza"

------

## POC to Production step

This document outlines the key considerations, best practices, and recommended tools for scaling a Retrieval-Augmented Generation (RAG) system from proof-of-concept to production.

## Table of Contents

1. [Data Ingestion & Preprocessing Pipeline](#data-ingestion--preprocessing-pipeline)
2. [Embedding Generation & Vector Store](#embedding-generation--vector-store)
3. [LLM Integration](#llm-integration)
4. [Retrieval & Generation Logic](#retrieval--generation-logic)
5. [Monitoring & Observability](#monitoring--observability)
6. [Deployment & Infrastructure](#deployment--infrastructure)
7. [A/B Testing & Iteration](#ab-testing--iteration)

---

## 1. Data Ingestion & Preprocessing Pipeline

### POC Scenario

* Manual file uploads and one-off scripts

### Production Requirements

* **Automation**: Use orchestration tools (Apache Airflow, Prefect, Kubeflow Pipelines, Cloud Functions) to fetch, transform, and load data regularly from multiple sources (databases, APIs, file storage)
* **Scalability**: Handle large volumes via distributed processing frameworks (e.g., Apache Spark) if needed
* **Data Validation & Cleaning**: Implement data quality checks, cleaning routines, and strict PII handling
* **Versioning**: Track data versions (e.g., with Delta Lake or DVC) to enable reproducibility and auditing

---

## 2. Embedding Generation & Vector Store

### POC Scenario

* Local embedding models (Sentence Transformers)
* On-disk vector stores (FAISS, ChromaDB)

### Production Requirements

* **Managed Vector Databases**: Pinecone, Weaviate, Milvus, Vertex AI Vector Search, AWS OpenSearch

  * Scalability to millions/billions of vectors
  * High availability, replication, and automated backups
  * Optimized indexing & search performance
  * Security & access control
* **Embedding Model Deployment**: Serve custom models via endpoints (SageMaker, Vertex AI, KServe) for independent scaling
* **Update Strategy**: Plan incremental or full re-indexing pipelines when data or models change

---

## 3. LLM Integration

### POC Scenario

* Direct API calls to OpenAI, Anthropic, etc.

### Production Requirements

* **API Gateway & Rate Limiting**: Protect and throttle requests, manage authentication
* **Cost Management**: Monitor usage, use caching, consider fine-tuned or smaller models for frequent tasks
* **Model Versioning & Fallbacks**: Support multiple model versions with automatic fallback on failures
* **Latency Optimization**: Enable streaming responses, use keep-alive connections

---

## 4. Retrieval & Generation Logic

### POC Scenario

* Simple top‑k similarity retrieval

### Production Requirements

* **Advanced Retrieval**: Implement re-ranking, hybrid search (semantic + keyword), query expansion
* **Prompt Management**: Centralize prompts, version control, and A/B test different templates
* **Context Management**: Summarize or filter context chunks to fit token limits
* **Guardrails & Safety**: Integrate content filters (e.g., NeMo Guardrails) to prevent hallucinations or sensitive data leakage

---

## 5. Monitoring & Observability

### POC Scenario

* Manual log inspection

### Production Requirements

* **Logging**: Centralize application logs (data ingestion, embedding, retrieval, LLM calls, user queries) in ELK/Stackdriver
* **Metrics**: Track key metrics (latency, retrieval precision/recall proxies, response quality, error rates, resource utilization)
* **Tracing**: Deploy distributed tracing (OpenTelemetry) for end‑to‑end request flows
* **Alerting**: Configure alerts for anomalies and critical failures
* **Dashboards**: Build visualization dashboards (Grafana, Kibana) for system health and user feedback

---

## 6. Deployment & Infrastructure

### POC Scenario

* Single VM or local environment

### Production Requirements

* **Containerization**: Package services with Docker
* **Orchestration**: Use Kubernetes or serverless platforms (AWS Lambda, GCP Cloud Run)
* **CI/CD Pipeline**: Automate tests, builds, and deployments via GitHub Actions, Jenkins, GitLab CI
* **Infrastructure as Code**: Manage resources with Terraform or CloudFormation

---

## 7. A/B Testing & Iteration

### POC Scenario

* Ad-hoc experiments

### Production Requirements

* **Experimentation Framework**: Systematically A/B test embedding models, prompts, and retrieval strategies
* **Feedback Loop**: Collect user ratings (thumbs up/down, comments) and integrate into continuous improvement cycles
* **Metrics Analysis**: Regularly review experiment results and iterate based on quantitative and qualitative feedback