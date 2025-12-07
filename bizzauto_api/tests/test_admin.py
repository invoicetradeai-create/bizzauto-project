import sys
import os
from uuid import uuid4

# Add the parent directory of this test file (bizzauto_api) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
from database import get_db, TestingSessionLocal, test_engine
from dependencies import get_current_admin, get_current_user
import sql_models
import pytest

# Setup test database
@pytest.fixture(name="session")
def session_fixture():
    # Create the table
    sql_models.Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    # Drop the table
    sql_models.Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        yield session
    
    # Mock admin user
    def override_get_current_admin():
        return sql_models.User(
            id=uuid4(),
            email="admin@bizzauto.com",
            role="admin",
            full_name="Super Admin"
        )
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_admin_analytics(client):
    response = client.get("/api/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_revenue" in data

def test_admin_whatsapp_stats(client):
    response = client.get("/api/admin/whatsapp-stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_sent" in data

def test_admin_users_list(client):
    response = client.get("/api/admin/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
