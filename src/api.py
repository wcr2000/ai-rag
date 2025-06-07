from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .rag_pipeline import RAGPipeline
from . import config # To ensure config is loaded

# Initialize FastAPI app
app = FastAPI(
    title="RAG Demo API",
    description="API for interacting with a Retrieval Augmented Generation pipeline.",
    version="0.1.0"
)

# --- Globals ---
# Initialize RAG Pipeline once when the API starts
# This can take a moment, so it's done at startup.
try:
    rag_pipeline_instance = RAGPipeline()
except RuntimeError as e:
    print(f"CRITICAL: Failed to initialize RAG Pipeline for API: {e}")
    print("The API will likely not function correctly. Ensure vector store is built.")
    rag_pipeline_instance = None # Set to None so we can check later

# --- Pydantic Models for Request/Response ---
class QueryRequest(BaseModel):
    query: str
    # top_k: int = config.K_RETRIEVED_DOCS # Example: allow overriding k

class AnswerResponse(BaseModel):
    answer: str
    source_documents: list = [] # List of dicts or simplified document representations

# --- API Endpoints ---
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QueryRequest):
    """
    Receives a query, processes it through the RAG pipeline, and returns the answer.
    """
    if rag_pipeline_instance is None:
        raise HTTPException(
            status_code=503, 
            detail="RAG Pipeline is not available. Service might be initializing or encountered an error."
        )
    
    try:
        result = rag_pipeline_instance.ask(request.query)
        # Format source documents for the response if needed
        formatted_sources = []
        if result.get("source_documents"):
            for doc in result["source_documents"]:
                formatted_sources.append({
                    "content_preview": doc.page_content[:200] + "...", # Preview
                    "metadata": doc.metadata
                })
        
        return AnswerResponse(answer=result["answer"], source_documents=formatted_sources)
    except Exception as e:
        # Log the exception e here for debugging
        print(f"Error during API request processing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your request: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Demo API. Use the /ask endpoint to submit queries."}

# --- Main block to run Uvicorn (for local development) ---
if __name__ == "__main__":
    # This allows running the API directly using `python src/api.py`
    # For production, you'd typically use `uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload`
    print("Starting FastAPI server with Uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8000)