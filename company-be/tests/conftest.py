import pytest
from fastapi.testclient import TestClient

from app.data.store import reset_store
from app.main import app


@pytest.fixture(autouse=True)
def reset_in_memory_store():
    """Reset the mock data store before and after each test."""
    reset_store()
    yield
    reset_store()


@pytest.fixture
def client():
    """FastAPI test client instance."""
    with TestClient(app) as test_client:
        yield test_client
