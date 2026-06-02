"""测试配置：使用 SQLite 文件数据库，无需 MySQL"""
import os
import pytest
from fastapi.testclient import TestClient

# === 在导入 app 前将数据库切换为 SQLite ===
TEST_DB_PATH = "test_account_book.db"
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

import app.config
app.config.Config.DATABASE_URL = f"sqlite:///{TEST_DB_PATH}?check_same_thread=False"

from app.database import engine, Base
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """每个测试会话开始时建表"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass


@pytest.fixture(autouse=True)
def clean_db():
    """每个测试函数前清空数据，避免测试间相互污染"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_category(client) -> dict:
    """创建一个测试分类并返回"""
    resp = client.post("/api/categories", json={
        "name": "测试分类",
        "type": "expense",
        "icon": "🧪",
        "color": "#000000",
    })
    return resp.json()


@pytest.fixture
def sample_income_category(client) -> dict:
    """创建一个收入测试分类"""
    resp = client.post("/api/categories", json={
        "name": "工资",
        "type": "income",
        "icon": "💰",
        "color": "#67C23A",
    })
    return resp.json()
