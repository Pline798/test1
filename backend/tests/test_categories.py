"""分类管理 API 测试"""
import pytest
from fastapi.testclient import TestClient


def test_list_categories_empty(client):
    """GET /api/categories 初始应返回列表（含种子数据）"""
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_create_category(client):
    """POST /api/categories 应创建新分类"""
    payload = {
        "name": "餐饮",
        "type": "expense",
        "icon": "🍜",
        "color": "#F56C6C",
    }
    resp = client.post("/api/categories", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "餐饮"
    assert data["type"] == "expense"
    assert data["id"] > 0
    assert "icon" in data
    assert "color" in data


def test_create_category_without_optional(client):
    """创建分类时 icon 和 color 应使用默认值"""
    resp = client.post("/api/categories", json={
        "name": "交通",
        "type": "expense",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["icon"] == "📁"
    assert data["color"] == "#409EFF"


def test_create_category_invalid_type(client):
    """创建分类时 type 不在 income/expense 范围内应报 422"""
    resp = client.post("/api/categories", json={
        "name": "无效",
        "type": "invalid",
    })
    assert resp.status_code == 422


def test_create_category_empty_name(client):
    """创建分类时名称为空应报 422"""
    resp = client.post("/api/categories", json={
        "name": "",
        "type": "expense",
    })
    assert resp.status_code == 422


def test_get_categories_by_type(client, sample_category, sample_income_category):
    """GET /api/categories?type=expense 应只返回支出分类"""
    resp = client.get("/api/categories?type=expense")
    assert resp.status_code == 200
    data = resp.json()
    assert all(c["type"] == "expense" for c in data)

    resp = client.get("/api/categories?type=income")
    assert resp.status_code == 200
    data = resp.json()
    assert all(c["type"] == "income" for c in data)


def test_update_category(client, sample_category):
    """PUT /api/categories/{id} 应更新分类"""
    cat_id = sample_category["id"]
    resp = client.put(f"/api/categories/{cat_id}", json={
        "name": "更新后的分类",
        "color": "#FF0000",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "更新后的分类"
    assert data["color"] == "#FF0000"


def test_update_category_not_found(client):
    """PUT /api/categories/{id} 不存在的分类应返回 404"""
    resp = client.put("/api/categories/99999", json={"name": "不存在"})
    assert resp.status_code == 404


def test_update_category_clear_description(client, sample_category):
    """PUT 应允许将字段更新为空字符串"""
    cat_id = sample_category["id"]
    # 先设置 icon
    client.put(f"/api/categories/{cat_id}", json={"icon": "✅"})
    # 再清空 icon（设为空字符串）
    resp = client.put(f"/api/categories/{cat_id}", json={"icon": ""})
    assert resp.status_code == 200
    assert resp.json()["icon"] == ""


def test_delete_category(client, sample_category):
    """DELETE /api/categories/{id} 应删除分类"""
    cat_id = sample_category["id"]
    resp = client.delete(f"/api/categories/{cat_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "删除成功"

    # 再次查询应返回 404
    resp = client.delete(f"/api/categories/{cat_id}")
    assert resp.status_code == 404


def test_delete_category_not_found(client):
    """DELETE /api/categories/{id} 不存在的分类应返回 404"""
    resp = client.delete("/api/categories/99999")
    assert resp.status_code == 404
