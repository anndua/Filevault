from collections.abc import Iterator
from io import BytesIO
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-only-secret-not-for-deployment")
os.environ.setdefault("ALGORITHM", "HS256")

from dependencies import get_rate_limiter, get_session, get_storage
from main import app
from services.rate_limiter import RateLimiter
from storage.base import storageBackend


class MemoryStorage(storageBackend):
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put(self, key: str, data: BytesIO) -> None:
        self.objects[key] = data.read()

    def get(self, key: str) -> BytesIO:
        return BytesIO(self.objects[key])

    def delete(self, key: str) -> None:
        del self.objects[key]

    def exists(self, key: str) -> bool:
        return key in self.objects

    def generate_download_url(self, key, expires_in, filename=None) -> str:
        return f"https://storage.test/{key}"


class MemoryRedis:
    def __init__(self) -> None:
        self.counters: dict[str, int] = {}

    def eval(self, _script: str, _key_count: int, key: str, _window: int):
        count = self.counters.get(key, 0) + 1
        self.counters[key] = count
        return count, 60


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture
def client(storage: MemoryStorage) -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_storage] = lambda: storage
    memory_redis = MemoryRedis()
    app.dependency_overrides[get_rate_limiter] = lambda: RateLimiter(memory_redis)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def register(client: TestClient, email: str) -> None:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "correct-horse-battery"},
    )
    assert response.status_code == 200, response.text


def login(client: TestClient, email: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": email, "password": "correct-horse-battery"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]
