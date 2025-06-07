from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import RetrievalQA

from . import config
from .vector_store import load_vector_store, get_embedding_model, search_vector_store
from .llm_handler import get_llm, get_rag_prompt_template

class RAGPipeline:
    def __init__(self):
        print("Initializing RAG Pipeline...")
        self.embeddings_model = get_embedding_model()
        self.vector_store = load_vector_store(
            index_path=str(config.VECTOR_STORE_PATH),
            embeddings_model=self.embeddings_model
        )
        
        if self.vector_store is None:
            # This is a critical failure for the RAG pipeline
            raise RuntimeError(
                "Failed to load vector store. "
                "Please ensure 'vector_store_index/faiss_index' exists and is valid. "
                "You might need to run the data ingestion/vector store creation process first."
            )
            
        self.llm = get_llm()
        self.prompt_template = get_rag_prompt_template()
        
        # Two ways to build the chain:
        # 1. Using Langchain's LCEL (LangChain Expression Language) - more flexible
        # self.rag_chain = self._build_rag_chain_lcel()
        
        # 2. Using a pre-built chain like RetrievalQA - simpler for standard RAG
        self.rag_chain = self._build_retrieval_qa_chain()
        
        print("RAG Pipeline initialized successfully.")

    def _build_rag_chain_lcel(self):
        """
        Builds the RAG chain using LangChain Expression Language (LCEL).
        """
        retriever = self.vector_store.as_retriever(search_kwargs={"k": config.K_RETRIEVED_DOCS})

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        return rag_chain

    def _build_retrieval_qa_chain(self):
        """
        Builds the RAG chain using the RetrievalQA chain.
        """
        retriever = self.vector_store.as_retriever(search_kwargs={"k": config.K_RETRIEVED_DOCS})
        
        # The chain_type "stuff" uses ALL text from documents in the context.
        # Other types like "map_reduce" or "refine" can be used for longer contexts.
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff", # "stuff", "map_reduce", "refine", "map_rerank"
            retriever=retriever,
            return_source_documents=True, # Optionally return source documents
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        return qa_chain

    def ask(self, query: str) -> dict:
        """
        Asks a question to the RAG pipeline.
        
        Returns a dictionary with 'answer' and optionally 'source_documents'.
        """
        if self.vector_store is None:
            return {"answer": "Error: Vector store not loaded. Cannot process query.", "source_documents": []}
        
        print(f"\nProcessing query: '{query}'")
        
        # If using LCEL chain:
        # response = self.rag_chain.invoke(query)
        # return {"answer": response, "source_documents": []} # LCEL chain needs manual source doc handling

        # If using RetrievalQA chain:
        response_payload = self.rag_chain.invoke({"query": query}) # RetrievalQA expects a dict with "query"
        answer = response_payload.get('result', "No answer found.")
        source_docs = response_payload.get('source_documents', [])
        
        print(f"LLM Answer: {answer}")
        if source_docs:
            print(f"\nSources ({len(source_docs)} documents found):")
            for i, doc in enumerate(source_docs):
                print(f"  Source {i+1}: {doc.metadata.get('source', 'N/A')} (Page: {doc.metadata.get('page', 'N/A')})")
                # print(f"    Content snippet: {doc.page_content[:150]}...")
        
        return {"answer": answer, "source_documents": source_docs}


if __name__ == '__main__':
    # This part is for demonstrating the RAG pipeline after the vector store is built.
    # You should run the build_vector_store.py (or equivalent main script part) first.
    
    print("Attempting to run RAG Pipeline...")
    try:
        rag_pipeline = RAGPipeline()
        
        # Test query
        test_query = "What is Retrieval Augmented Generation?"
        result = rag_pipeline.ask(test_query)
        print(f"\nFinal Answer for '{test_query}':\n{result['answer']}")

        test_query_2 = "How does RAG help LLMs?"
        result_2 = rag_pipeline.ask(test_query_2)
        print(f"\nFinal Answer for '{test_query_2}':\n{result_2['answer']}")
        
        test_query_3 = "What is the capital of France?" # Should say it doesn't know or from context
        result_3 = rag_pipeline.ask(test_query_3)
        print(f"\nFinal Answer for '{test_query_3}':\n{result_3['answer']}")

    except RuntimeError as e:
        print(f"Runtime Error during RAG pipeline execution: {e}")
        print("Please ensure the vector store is built first. You can run 'python main.py build' to create it.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")