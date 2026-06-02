"""分类管理 API 测试"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_list_categories(client):
    """GET /api/categories 应返回分类列表"""
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_category(client):
    """POST /api/categories 应创建新分类"""
    payload = {
        "name": "测试分类",
        "type": "expense",
        "icon": "🧪",
        "color": "#000000",
    }
    resp = client.post("/api/categories", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "测试分类"
    assert data["id"] > 0
