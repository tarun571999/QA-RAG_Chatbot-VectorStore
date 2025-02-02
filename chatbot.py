import os
import logging
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, faiss_index_path: str):
        """
        Initializes the Chatbot with FAISS index and OpenAI API.

        Args:
            faiss_index_path (str): Path to the directory containing the FAISS index.
        """
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is not set in the environment variables.")

        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)

        # Load FAISS vector store
        self.vector_store = self.load_faiss_index(faiss_index_path)

        # Maintain chat history for contextual conversations
        self.chat_history = []  

    def load_faiss_index(self, faiss_index_path: str):
        """
        Loads FAISS index from the specified directory.

        Args:
            faiss_index_path (str): Path to the directory containing the FAISS index.

        Returns:
            FAISS: The loaded FAISS index.
        """
        try:
            index_file = os.path.join(faiss_index_path, "index.faiss")
            if not os.path.exists(index_file):
                raise FileNotFoundError(f"FAISS index file not found at {index_file}")

            logger.info(f"Loading FAISS index from {faiss_index_path}")
            return FAISS.load_local(faiss_index_path, self.embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            return None  # Ensure None is returned explicitly

    def get_answer(self, query: str):
        """
        Retrieves relevant documents from FAISS and generates a response using OpenAI.

        Args:
            query (str): The user's query.

        Returns:
            str: The chatbot's response.
        """
        try:
            if self.vector_store is None:
                return "FAISS vector store is not loaded."

            # Retrieve relevant documents with scores
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=3)

            # Set a threshold for filtering low-score documents
            threshold = 0.5  
            relevant_docs = [doc for doc, score in docs_with_scores if score < threshold]

            if not relevant_docs:
                return "No relevant documents found."

            docs_page_content = "\n".join([doc.page_content for doc in relevant_docs])

            # Format conversation history
            history_str = "\n".join([f"User: {q}\nBot: {a}" for q, a in self.chat_history])

            # Escape curly braces in chat prompt
            chat_template = ChatPromptTemplate.from_messages([
                ("user", f"Here is the conversation history:\n{history_str}\n\nNow answer:\n{query}\n\nContext: {docs_page_content.replace('{', '{{').replace('}', '}}')}")
            ])

            # Generate response
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=self.openai_api_key)
            chain = LLMChain(llm=llm, prompt=chat_template, output_key="answer")
            response = chain({"question": query, "docs": docs_page_content})

            # Save chat history
            self.chat_history.append((query, response["answer"]))
            # Clean up the response (render markdown properly for the frontend)
            formatted_answer = response["answer"]
            formatted_answer = formatted_answer.replace("\n", "<br>")  # HTML line breaks

            return formatted_answer
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Sorry, an error occurred: {str(e)}"