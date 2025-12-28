import pytest
from app.services.chat_service import ChatService
from app.models.response_models import ChatResponse

@pytest.fixture
def chat_service():
    return ChatService()

def test_search_products(chat_service):
    session_id = "test_session_123"
    response = chat_service.generate_response("Find me a smartphone", session_id)
    assert isinstance(response, ChatResponse)
    assert len(response.response) > 0
    assert isinstance(response.response, str)

def test_order_status(chat_service):
    session_id = "test_session_123" 
    response = chat_service.generate_response("What is the status of order 12345?", session_id)
    assert isinstance(response, ChatResponse)
    assert len(response.response) > 0
    assert isinstance(response.response, str)