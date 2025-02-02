import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from markdown_it import MarkdownIt
import re
from utils import log_info, log_error  

# Load environment variables
load_dotenv()

class VectorStore:
    def __init__(self, docs_path, chunk_size=1000, chunk_overlap=100):
        """
        Initializes the VectorStore for FAISS indexing using OpenAI embeddings.

        Args:
            docs_path (str): Path to the directory containing Markdown files.
            chunk_size (int): Size of text chunks for embeddings.
            chunk_overlap (int): Overlap between text chunks.
        """
        self.docs_path = docs_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Load OpenAI API key from .env or environment variable
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is missing. Set 'OPENAI_API_KEY' in environment variables.")

        # Initialize OpenAI Embeddings
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-ada-002",  # Best suited for FAISS
            openai_api_key=self.openai_api_key
        )

        # Initialize markdown parser
        self.md_parser = MarkdownIt()

        # Initialize text splitter (using RecursiveCharacterTextSplitter)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )

    def load_markdown_files(self):
        """
        Recursively loads all markdown files from subdirectories of 'docs_path'.
        
        Returns:
            dict: Mapping of file paths to their cleaned markdown content.
        """
        md_documents = {}

        for root, _, files in os.walk(self.docs_path):
            for file in files:
                if file.endswith(".md"):  # Process only markdown files
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw_text = f.read()
                        cleaned_text = self.md_parser.parse(raw_text)
                        md_documents[file_path] = "\n".join(node.content for node in cleaned_text if hasattr(node, 'content'))
        
        log_info(f"Loaded {len(md_documents)} markdown files from {self.docs_path}")
        return md_documents

    def intelligent_chunking(self, md_documents):
        """
        Splits markdown files into chunks intelligently by prioritizing headers,
        then splitting by sentences.

        Args:
            md_documents (dict): Mapping of file paths to parsed markdown content.

        Returns:
            list: List of chunked documents with text and source metadata.
        """
        chunked_docs = []

        header_pattern = re.compile(r"^(#{1,6})\s")  # Regex to detect headers (e.g., #, ##, ###)

        for file_path, content in md_documents.items():
            chunks = []
            lines = content.split("\n")
            current_chunk = []

            for line in lines:
                if header_pattern.match(line):  # If header found, split here
                    if current_chunk:
                        chunks.append("".join(current_chunk))  # Add previous chunk
                    current_chunk = [line]  # Start a new chunk with the header
                else:
                    current_chunk.append(line)  # Add line to the current chunk

            if current_chunk:  # Add the last chunk
                chunks.append("".join(current_chunk))

            # Now split further by sentences if chunks are too large
            for chunk in chunks:
                text_chunks = self.text_splitter.split_text(chunk)  # Use RecursiveCharacterTextSplitter here
                for text_chunk in text_chunks:
                    chunked_docs.append({"text": text_chunk, "source": file_path})

        return chunked_docs

    def store_embeddings_in_faiss(self, chunked_docs):
        """
        Stores document chunks in FAISS with metadata for better retrieval.

        Args:
            chunked_docs (list): List of chunked documents with text and source metadata.

        Returns:
            FAISS: The FAISS index.
        """
        docs = [Document(page_content=chunk["text"], metadata={"source": chunk["source"]}) for chunk in chunked_docs]

        # Create FAISS vector store
        faiss_index = FAISS.from_documents(docs, self.embedding_model)

        # Save FAISS index locally
        faiss_index_dir = "faiss_index"
        os.makedirs(faiss_index_dir, exist_ok=True)
        faiss_index.save_local(faiss_index_dir)

        log_info(f"FAISS index created and saved at '{faiss_index_dir}'")
        return faiss_index

    def process_and_store_docs(self):
        """
        Processes documents, generates FAISS vector store, and saves it.
        """
        try:
            md_documents = self.load_markdown_files()
            if not md_documents:
                raise ValueError("No Markdown documents found in the directory.")

            chunked_docs = self.intelligent_chunking(md_documents)  # Updated chunking
            faiss_index = self.store_embeddings_in_faiss(chunked_docs)

            log_info("FAISS vector store has been successfully created!")
        except Exception as e:
            log_error(f"Error during FAISS index creation: {str(e)}")


if __name__ == "__main__":
    docs_path = "ubuntu-docs"  # Set this to the directory with your markdown files

    # Initialize and run the VectorStore
    vector_store = VectorStore(docs_path)
    vector_store.process_and_store_docs()