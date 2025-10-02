from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_books():
    r = client.get("/books")
    assert r.status_code == 200
    assert isinstance(r.json(), list) or isinstance(r.json(), dict)

def test_stats_general():
    r = client.get("/stats/general")
    assert r.status_code == 200
    assert "average_price" in r.json()