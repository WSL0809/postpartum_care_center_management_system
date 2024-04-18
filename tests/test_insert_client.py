from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth import get_current_active_user
from auth_schema import User
from database import get_db, SessionLocal
from main import app
import pytest



# Fixture用于测试客户端
@pytest.fixture(scope="module")
def client():
    # 重写依赖项
    def override_get_db():
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


# 模拟一个活跃的管理员用户
@pytest.fixture(scope="module")
def admin_user():
    user = User(username="admin", role="admin", active=True)
    return user


# 测试用例：尝试插入一个新客户
def test_insert_client_success(client, admin_user):
    app.dependency_overrides[get_current_active_user] = lambda: admin_user
    response = client.post("/insert_client", json={
        "id_number": "12345678",
        "name": "Test User",
        "tel": "1234567890",
        "age": 30,
        "scheduled_date": "2023-01-01",
        "check_in_date": None,
        "hospital_for_childbirth": "Test Hospital",
        "contact_name": "Test Contact",
        "contact_tel": "0987654321",
        "meal_plan_id": 2,
        "mode_of_delivery": "Natural"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
