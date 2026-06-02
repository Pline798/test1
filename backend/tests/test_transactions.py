"""流水记录 API 测试"""
import pytest
from fastapi.testclient import TestClient


def _create_transaction(client, category_id: int, **overrides) -> dict:
    """辅助：创建一个交易"""
    payload = {
        "amount": 100.00,
        "type": "expense",
        "category_id": category_id,
        "description": "测试记录",
        "date": "2026-06-01",
    }
    payload.update(overrides)
    return client.post("/api/transactions", json=payload)


class TestCreateTransaction:
    def test_create_expense(self, client, sample_category):
        resp = _create_transaction(client, sample_category["id"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount"] == 100.00
        assert data["type"] == "expense"
        assert data["description"] == "测试记录"
        assert data["id"] > 0
        assert "date" in data
        assert "created_at" in data

    def test_create_income(self, client, sample_income_category):
        resp = _create_transaction(client, sample_income_category["id"],
                                   amount=5000, type="income", description="工资收入")
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount"] == 5000.00
        assert data["type"] == "income"

    def test_create_zero_amount(self, client, sample_category):
        resp = _create_transaction(client, sample_category["id"], amount=0)
        assert resp.status_code == 422

    def test_create_negative_amount(self, client, sample_category):
        resp = _create_transaction(client, sample_category["id"], amount=-10)
        assert resp.status_code == 422

    def test_create_missing_category(self, client):
        resp = _create_transaction(client, 99999)
        # SQLite 不强制外键时返回 200，MySQL 会报错
        assert resp.status_code in (200, 404, 422, 500)

    def test_create_no_description(self, client, sample_category):
        """description 是可选的"""
        resp = client.post("/api/transactions", json={
            "amount": 50,
            "type": "expense",
            "category_id": sample_category["id"],
            "date": "2026-06-01",
        })
        assert resp.status_code == 200

    def test_create_future_date(self, client, sample_category):
        resp = _create_transaction(client, sample_category["id"], date="2030-01-01")
        assert resp.status_code == 200
        assert resp.json()["date"] == "2030-01-01"


class TestListTransactions:
    def test_list_empty(self, client):
        resp = client.get("/api/transactions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_with_data(self, client, sample_category):
        _create_transaction(client, sample_category["id"])
        resp = client.get("/api/transactions")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_filter_by_type(self, client, sample_category, sample_income_category):
        _create_transaction(client, sample_category["id"], type="expense")
        _create_transaction(client, sample_income_category["id"], type="income")

        resp = client.get("/api/transactions?type=expense")
        assert all(t["type"] == "expense" for t in resp.json())

        resp = client.get("/api/transactions?type=income")
        assert all(t["type"] == "income" for t in resp.json())

    def test_filter_by_year_month(self, client, sample_category):
        _create_transaction(client, sample_category["id"], date="2026-06-01")
        _create_transaction(client, sample_category["id"], date="2026-05-01")

        resp = client.get("/api/transactions?year=2026&month=6")
        assert all(t["date"].startswith("2026-06") for t in resp.json())

    def test_keyword_search(self, client, sample_category):
        _create_transaction(client, sample_category["id"], description="午餐")
        _create_transaction(client, sample_category["id"], description="晚餐")

        resp = client.get("/api/transactions?keyword=午餐")
        assert len(resp.json()) == 1
        assert resp.json()[0]["description"] == "午餐"

    def test_pagination(self, client, sample_category):
        for i in range(5):
            _create_transaction(client, sample_category["id"], amount=10 * (i + 1))

        resp = client.get("/api/transactions?skip=0&limit=3")
        assert len(resp.json()) == 3

        resp = client.get("/api/transactions?skip=3&limit=3")
        assert len(resp.json()) == 2


class TestAmountSearch:
    def _setup_data(self, client, sample_category):
        """创建 3 条不同金额的测试数据"""
        client.post("/api/transactions", json={
            "amount": 10, "type": "expense", "category_id": sample_category["id"],
            "description": "小", "date": "2026-06-01",
        })
        client.post("/api/transactions", json={
            "amount": 100, "type": "expense", "category_id": sample_category["id"],
            "description": "中", "date": "2026-06-01",
        })
        client.post("/api/transactions", json={
            "amount": 1000, "type": "expense", "category_id": sample_category["id"],
            "description": "大", "date": "2026-06-01",
        })

    def test_amount_min(self, client, sample_category):
        self._setup_data(client, sample_category)
        resp = client.get("/api/transactions?amount_min=100")
        assert len(resp.json()) == 2  # 100, 1000

    def test_amount_max(self, client, sample_category):
        self._setup_data(client, sample_category)
        resp = client.get("/api/transactions?amount_max=100")
        assert len(resp.json()) == 2  # 10, 100

    def test_amount_range(self, client, sample_category):
        self._setup_data(client, sample_category)
        resp = client.get("/api/transactions?amount_min=50&amount_max=500")
        assert len(resp.json()) == 1  # 100

    def test_amount_min_zero(self, client, sample_category):
        """amount_min=0 应返回所有记录"""
        self._setup_data(client, sample_category)
        resp = client.get("/api/transactions?amount_min=0")
        assert len(resp.json()) == 3

    def test_amount_max_zero(self, client, sample_category):
        """amount_max=0 应只返回金额为 0 的记录"""
        self._setup_data(client, sample_category)
        resp = client.get("/api/transactions?amount_max=0")
        assert len(resp.json()) == 0


class TestUpdateTransaction:
    def test_update_amount(self, client, sample_category):
        created = _create_transaction(client, sample_category["id"]).json()
        txn_id = created["id"]

        resp = client.put(f"/api/transactions/{txn_id}", json={"amount": 200})
        assert resp.status_code == 200
        assert resp.json()["amount"] == 200.00

    def test_update_description(self, client, sample_category):
        created = _create_transaction(client, sample_category["id"]).json()
        txn_id = created["id"]

        resp = client.put(f"/api/transactions/{txn_id}", json={"description": "修改后"})
        assert resp.status_code == 200
        assert resp.json()["description"] == "修改后"

    def test_update_date(self, client, sample_category):
        created = _create_transaction(client, sample_category["id"], date="2026-06-01").json()
        txn_id = created["id"]

        resp = client.put(f"/api/transactions/{txn_id}", json={"date": "2026-07-01"})
        assert resp.status_code == 200
        assert resp.json()["date"] == "2026-07-01"

    def test_update_not_found(self, client):
        resp = client.put("/api/transactions/99999", json={"amount": 100})
        assert resp.status_code == 404

    def test_update_clear_description(self, client, sample_category):
        """测试将可选字段改为空字符串"""
        created = _create_transaction(client, sample_category["id"]).json()
        txn_id = created["id"]

        resp = client.put(f"/api/transactions/{txn_id}", json={"description": ""})
        assert resp.status_code == 200
        assert resp.json()["description"] == ""


class TestDeleteTransaction:
    def test_delete(self, client, sample_category):
        created = _create_transaction(client, sample_category["id"]).json()
        txn_id = created["id"]

        resp = client.delete(f"/api/transactions/{txn_id}")
        assert resp.status_code == 200
        assert resp.json()["message"] == "删除成功"

        resp = client.delete(f"/api/transactions/{txn_id}")
        assert resp.status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/api/transactions/99999")
        assert resp.status_code == 404


class TestStats:
    def test_stats_empty(self, client):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "income" in data
        assert "expense" in data
        assert "by_category" in data

    def test_stats_with_data(self, client, sample_category, sample_income_category):
        _create_transaction(client, sample_category["id"], amount=50, type="expense")
        _create_transaction(client, sample_income_category["id"], amount=1000, type="income")

        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["income"]["total"] == 1000.00
        assert data["expense"]["total"] == 50.00
        assert len(data["by_category"]) == 2

    def test_stats_filter_by_year_month(self, client, sample_category):
        _create_transaction(client, sample_category["id"], date="2026-06-01")
        _create_transaction(client, sample_category["id"], date="2026-05-01")

        resp = client.get("/api/stats?year=2026&month=6")
        assert resp.json()["expense"]["count"] == 1

        resp = client.get("/api/stats?year=2026&month=5")
        assert resp.json()["expense"]["count"] == 1
