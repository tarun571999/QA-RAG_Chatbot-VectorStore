from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from chatbot import Chatbot
from uuid import uuid4

app = FastAPI()

# Store chatbots per session ID
chatbot_sessions = {}

class QueryRequest(BaseModel):
    session_id: str  
    question: str

@app.post("/chat")
async def chat(request: QueryRequest):
    """
    Handles user queries and returns responses from the chatbot.

    Args:
        request (QueryRequest): The request containing the session ID and user question.

    Returns:
        dict: The response containing the session ID, question, and answer.
    """
    try:
        # Create new session if not exists
        if request.session_id not in chatbot_sessions:
            chatbot_sessions[request.session_id] = Chatbot("faiss_index")

        chatbot = chatbot_sessions[request.session_id]
        response = chatbot.get_answer(request.question)

        return {"session_id": request.session_id, "question": request.question, "answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/new_session")
async def new_session():
    """
    Generates a new session ID for a user.

    Returns:
        dict: The newly generated session ID.
    """
    session_id = str(uuid4())
    return {"session_id": session_id}