from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_endpoint():
    response = client.post("/chat/ask", json={"message": "Find me a smartphone", "session_id": "test_session"})
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        response_data = response.json()
        assert "response" in response_data
        assert len(response_data["response"]) > 0

def test_order_status_endpoint():
    response = client.post("/chat/order-status", json={"order_id": "12345", "session_id": "test_session"})
    assert response.status_code in [200, 401, 404]
    if response.status_code == 200:
        response_data = response.json()
        assert "status" in response_data or "response" in response_data