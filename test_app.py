import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_create_event(client):
    response = client.post('/events', json={
        "title": "Test Event",
        "description": "Testing create",
        "start_time": "2025-06-30T10:00:00",
        "end_time": "2025-06-30T11:00:00"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == "Test Event"

def test_get_events(client):
    response = client.get('/events')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
