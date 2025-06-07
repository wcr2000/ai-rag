import unittest
from pathlib import Path
import tempfile
import shutil

from src.data_processor import load_documents_from_directory, split_documents_into_chunks
from langchain.docstore.document import Document as LangchainDocument

class TestDataProcessor(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_txt_file = self.test_dir / "test_doc.txt"
        self.test_pdf_file = self.test_dir / "test_doc.pdf" # PDF testing is more complex, requires a sample PDF

        # Create a sample text file
        with open(self.test_txt_file, "w") as f:
            f.write("This is a test document. It has multiple sentences.\nSecond line for chunking.")
        
        # For PDF, you'd need a small PDF file. For now, we'll skip detailed PDF content testing
        # or assume pypdf handles it correctly.

    def tearDown(self):
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_load_txt_documents(self):
        documents = load_documents_from_directory(self.test_dir)
        self.assertEqual(len(documents), 1) # Expecting only the .txt file to be loaded simply
        self.assertIsInstance(documents[0], LangchainDocument)
        self.assertIn("This is a test document", documents[0].page_content)
        self.assertEqual(documents[0].metadata["source"], "test_doc.txt")

    def test_split_documents(self):
        doc_content = "This is a long string of text that is definitely longer than ten characters and should be split into multiple chunks if the chunk size is small enough. Let's make it even longer to be sure."
        doc = LangchainDocument(page_content=doc_content, metadata={"source": "test_split.txt"})
        
        # Test with a small chunk size
        chunks = split_documents_into_chunks([doc], chunk_size=20, chunk_overlap=5)
        self.assertTrue(len(chunks) > 1)
        for chunk in chunks:
            self.assertIsInstance(chunk, LangchainDocument)
            self.assertTrue(len(chunk.page_content) <= 20 + 5) # Allow for some leeway due to overlap logic

        # Test with a large chunk size (should result in 1 chunk)
        chunks_large = split_documents_into_chunks([doc], chunk_size=500, chunk_overlap=50)
        self.assertEqual(len(chunks_large), 1)
        self.assertEqual(chunks_large[0].page_content, doc_content)

    def test_load_empty_directory(self):
        empty_dir = self.test_dir / "empty_subdir"
        empty_dir.mkdir()
        documents = load_documents_from_directory(empty_dir)
        self.assertEqual(len(documents), 0)

    def test_load_unsupported_file(self):
        unsupported_file = self.test_dir / "image.jpg"
        with open(unsupported_file, "w") as f: # Create a dummy file
            f.write("fake image data")
        
        # Add a valid .txt file so we load at least one document
        valid_txt_file = self.test_dir / "another.txt"
        with open(valid_txt_file, "w") as f:
            f.write("valid text")
            
        documents = load_documents_from_directory(self.test_dir)
        # Should load only 'test_doc.txt' and 'another.txt'
        # The exact number depends on how many files are in test_dir initially
        # Check that 'image.jpg' is not in metadata sources
        sources = [doc.metadata["source"] for doc in documents]
        self.assertNotIn("image.jpg", sources)
        self.assertIn("test_doc.txt", sources)
        self.assertIn("another.txt", sources)


if __name__ == '__main__':
    unittest.main()