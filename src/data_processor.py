import os
from pathlib import Path
from typing import List, Union

from langchain.docstore.document import Document as LangchainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from . import config

def load_documents_from_directory(directory_path: Union[str, Path]) -> List[LangchainDocument]:
    """
    Loads documents from the specified directory.
    Supports .txt and .pdf files.
    """
    documents = []
    path = Path(directory_path)
    if not path.is_dir():
        raise ValueError(f"Provided path {directory_path} is not a directory.")

    for file_path in path.iterdir():
        content = ""
        metadata = {"source": str(file_path.name)}
        if file_path.suffix == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append(LangchainDocument(page_content=content, metadata=metadata))
        elif file_path.suffix == ".pdf":
            try:
                reader = PdfReader(file_path)
                for page_num, page in enumerate(reader.pages):
                    content = page.extract_text()
                    if content: # Ensure there's text on the page
                        doc_metadata = metadata.copy()
                        doc_metadata["page"] = page_num + 1
                        documents.append(LangchainDocument(page_content=content, metadata=doc_metadata))
            except Exception as e:
                print(f"Error reading PDF {file_path.name}: {e}")
        else:
            print(f"Unsupported file type: {file_path.name}. Skipping.")
            
    if not documents:
        print(f"No documents loaded from {directory_path}. Ensure it contains .txt or .pdf files.")
    return documents

def split_documents_into_chunks(
    documents: List[LangchainDocument],
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP
) -> List[LangchainDocument]:
    """
    Splits a list of Langchain Documents into smaller chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True, # Useful for some applications
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def clean_text(text: str) -> str:
    """
    Basic text cleaning. (Optional, can be expanded)
    """
    text = text.strip()
    # Add more cleaning steps if needed, e.g., removing multiple spaces, special characters
    return text

if __name__ == '__main__':
    # Example usage:
    print(f"Loading documents from: {config.DATA_PATH}")
    raw_documents = load_documents_from_directory(config.DATA_PATH)
    
    if raw_documents:
        print(f"Loaded {len(raw_documents)} documents.")
        for doc in raw_documents:
            print(f"  - {doc.metadata['source']} (First 100 chars: {doc.page_content[:100].strip()}...)")
            # Apply cleaning if needed
            # doc.page_content = clean_text(doc.page_content)

        chunks = split_documents_into_chunks(raw_documents)
        print(f"\nFirst chunk example:\n{chunks[0].page_content}")
        print(f"Metadata: {chunks[0].metadata}")
    else:
        print("No documents were loaded. Please check the data directory and file types.")