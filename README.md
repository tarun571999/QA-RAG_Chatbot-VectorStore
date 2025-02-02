# Q&A Chatbot with Vector Store

## Overview
This project is a Q&A chatbot that uses a vector store and a Language Model (LLM) to answer user queries based on the provided Ubuntu documentation in markdown format. It uses FAISS for the vector store and OpenAI's embeddings for the language model, creating a robust and scalable retrieval-augmented generation (RAG) system.

## Features
- **Vector Store**: The system uses FAISS to store document embeddings and provide fast document retrieval based on user queries.
- **Language Model Integration**: Uses OpenAI's embeddings and a chat-based LLM to generate meaningful responses.
- **FastAPI Backend**: Exposes an API endpoint to interact with the chatbot through HTTP requests, with Swagger UI for easy testing and documentation.
- **Dockerized Solution**: The entire application can be deployed using Docker for easy scalability and portability.

## Technologies Used
- **Vector Store**: FAISS
- **Embedding Model**: OpenAI (text-embedding-ada-002)
- **Web Framework**: FastAPI
- **Containerization**: Docker
- **Logging**: Python Logging module

## Installation

Install dependencies: Install the required dependencies using pip:
pip install -r requirements.txt

### Steps to Run the Application

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your_username/QA-RAG_Chatbot-VectorStore.git
   cd QA-RAG_Chatbot-VectorStore

2. **Create a Virtual Environment (Optional)**

python -m venv venv
venv\Scripts\activate     # On Windows

3. **Install Dependencies**
pip install -r requirements.txt

### Creating FAISS Vector Store
Run the following command to process Ubuntu docs and store embeddings:
python vector_store.py

### Running the Chatbot API
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

### API Endpoints
GET	/new_session	Generates a new chat session ID
POST	/chat	Accepts a session ID & user query, returns chatbot response


### Chunking Strategy
Current Implementation:

    Recursive Character Text Splitter:
        Uses a fixed chunk size of 1000 tokens with an overlap of 100 tokens to ensure continuity between chunks.
        Implemented using LangChain's RecursiveCharacterTextSplitter, which ensures context-aware chunking.
    Header-Based Splitting:
        Detects markdown headers (#, ##, etc.) and uses them as natural breakpoints.
        This ensures that each chunk is semantically meaningful rather than arbitrarily split.
    Sentence-Based Refinement:
        After header-based splitting, if a chunk exceeds the limit, it is further split using RecursiveCharacterTextSplitter to maintain consistency.
    Metadata Storage:
        Each chunk retains the source file name as metadata, ensuring traceability during retrieval.


### Parse Documents
Current Implementation:
Markdown Parsing (MarkdownIt):

    Extracts clean, structured content from markdown files.
    Removes extraneous characters while preserving formatting (headers, lists, code blocks).

Recursive Directory Traversal (os.walk):

    Recursively searches all subdirectories in ubuntu-docs/ for .md files.
    Ensures no markdown files are missed during indexing.

Regex-Based Header Detection (re.compile):

    Identifies markdown headers (#, ##, etc.) for semantic chunking.
    Splits text intelligently at key points, rather than breaking mid-paragraph.

    
### Author
Tharun Kumar T
[LinkedIn](https://www.linkedin.com/in/tharun-kumar-t/)