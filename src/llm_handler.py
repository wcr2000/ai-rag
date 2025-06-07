from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from . import config

def get_llm():
    """
    Initializes and returns the Language Model (LLM).
    """
    llm = ChatOpenAI(
        model_name=config.LLM_MODEL_NAME,
        temperature=0.7, # Adjust for creativity vs. factuality
        openai_api_key=config.OPENAI_API_KEY
    )
    return llm

def get_rag_prompt_template() -> ChatPromptTemplate:
    """
    Returns a ChatPromptTemplate for the RAG chain.
    """
    template = """
    You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.
    Keep the answer concise and based ONLY on the provided context.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt


# This function demonstrates a basic LLM call without RAG, useful for testing the LLM connection.
def ask_llm_directly(llm, question: str) -> str:
    """
    Sends a question directly to the LLM without any context retrieval.
    """
    prompt = PromptTemplate.from_template("Question: {question}\nAnswer:")
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": question})
    return response


if __name__ == '__main__':
    print("Testing LLM Handler...")
    my_llm = get_llm()
    
    # Test direct LLM call
    test_question_direct = "What is the capital of France?"
    print(f"\nAsking LLM directly: '{test_question_direct}'")
    direct_answer = ask_llm_directly(my_llm, test_question_direct)
    print(f"LLM (direct) Answer: {direct_answer}")

    # Test RAG prompt template (just to see the structure)
    rag_prompt = get_rag_prompt_template()
    formatted_prompt = rag_prompt.format_messages(
        context="The Eiffel Tower is in Paris. Paris is a city in France.",
        question="Where is the Eiffel Tower?"
    )
    print("\nFormatted RAG Prompt example:")
    for msg in formatted_prompt:
        print(f"Type: {msg.type}, Content: {msg.content}")