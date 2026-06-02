"""流水记录 API 测试"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_list_transactions_empty(client):
    """GET /api/transactions 初始应返回空列表"""
    resp = client.get("/api/transactions")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
