import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.services.chat_service import ChatService
from app.models.response_models import ChatResponse

def test_memory():
    chat_service = ChatService()
    session_id = "test_session_123"
    
    response1 = chat_service.generate_response("Find me a smartphone", session_id)
    response2 = chat_service.generate_response("What did I ask earlier?", session_id)
    
    assert isinstance(response1, ChatResponse)
    assert isinstance(response2, ChatResponse)
    assert len(response1.response) > 0
    assert len(response2.response) > 0

if __name__ == "__main__":
    test_memory()