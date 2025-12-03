import sys
import os

# Add the parent directory of this test file (bizzauto_api) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
from database import get_db, TestingSessionLocal, test_engine
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
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_read_sales_summary(client):
    response = client.get("/api/accounting/sales_summary")
    assert response.status_code == 200
    assert isinstance(response.json(), list)