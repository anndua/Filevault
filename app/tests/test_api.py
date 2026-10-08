from fastapi.testclient import TestClient

from dependencies import get_rate_limiter
import services.share_service as share_service_module
from services.rate_limiter import RateLimiter
from tests.conftest import MemoryRedis, MemoryStorage, login, register
from storage.exceptions import StorageError


def test_health_and_openapi_are_available(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert client.get("/openapi.json").json()["info"]["title"] == "Filevault API"


def test_register_login_and_current_user(client: TestClient) -> None:
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_invalid_token_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401


def test_direct_upload_lists_metadata_and_enforces_owner(
    client: TestClient,
) -> None:
    register(client, "alice@example.com")
    register(client, "bob@example.com")
    alice_token = login(client, "alice@example.com")
    bob_token = login(client, "bob@example.com")
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    response = client.post(
        "/files/upload",
        headers=alice_headers,
        files={"file": ("note.txt", b"file bytes", "text/plain")},
    )
    assert response.status_code == 200, response.text
    file_id = response.json()["id"]

    metadata = client.get(f"/files/{file_id}", headers=alice_headers)
    assert metadata.status_code == 200
    assert metadata.json()["size"] == len(b"file bytes")
    assert metadata.json()["filename"] == "note.txt"

    listing = client.get("/files/", headers=alice_headers)
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()["items"]] == [file_id]

    assert client.get(f"/files/{file_id}", headers=bob_headers).status_code == 403
    assert client.get("/files/", headers=bob_headers).json()["total"] == 0
    assert client.get(f"/files/{file_id}/download", headers=bob_headers).status_code == 403
    assert client.delete(f"/files/{file_id}", headers=bob_headers).status_code == 403

    download = client.get(f"/files/{file_id}/download", headers=alice_headers)
    assert download.status_code == 200
    assert download.json()["url"].startswith("https://storage.test/")

    deleted = client.delete(f"/files/{file_id}", headers=alice_headers)
    assert deleted.status_code == 200
    assert client.get(f"/files/{file_id}", headers=alice_headers).status_code == 404


def test_chunked_upload_checks_owner_and_preserves_bytes_and_size(
    client: TestClient,
    storage: MemoryStorage,
) -> None:
    register(client, "alice@example.com")
    register(client, "bob@example.com")
    alice_token = login(client, "alice@example.com")
    bob_token = login(client, "bob@example.com")
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    initiated = client.post(
        "/uploads/initiate",
        headers=alice_headers,
        json={"filename": "large.bin", "total_chunks": 2},
    )
    assert initiated.status_code == 200, initiated.text
    upload_id = initiated.json()["upload_id"]

    assert client.post(
        f"/uploads/{upload_id}/chunks/1",
        headers=bob_headers,
        files={"file": ("chunk", b"first", "application/octet-stream")},
    ).status_code == 404
    assert client.post(
        f"/uploads/{upload_id}/complete",
        headers=bob_headers,
    ).status_code == 404

    first = b"first chunk "
    second = b"second chunk"
    for index, contents in enumerate((first, second), start=1):
        response = client.post(
            f"/uploads/{upload_id}/chunks/{index}",
            headers=alice_headers,
            files={"file": ("chunk", contents, "application/octet-stream")},
        )
        assert response.status_code == 200, response.text

    completed = client.post(
        f"/uploads/{upload_id}/complete",
        headers=alice_headers,
    )
    assert completed.status_code == 200, completed.text

    files = client.get("/files/", headers=alice_headers).json()["items"]
    uploaded = next(file for file in files if file["filename"] == "large.bin")
    assert uploaded["size"] == len(first) + len(second)
    metadata = client.get(f"/files/{uploaded['id']}", headers=alice_headers).json()
    assert storage.objects[metadata["object_key"]] == first + second


def test_chunk_completion_requires_all_chunks(client: TestClient) -> None:
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    initiated = client.post(
        "/uploads/initiate",
        headers=headers,
        json={"filename": "incomplete.bin", "total_chunks": 1},
    )
    upload_id = initiated.json()["upload_id"]
    response = client.post(f"/uploads/{upload_id}/complete", headers=headers)

    assert response.status_code == 400


def test_file_listing_paginates_searches_and_sorts(client: TestClient) -> None:
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    for filename, data in (("beta.txt", b"12"), ("Alpha.txt", b"1234"), ("other.bin", b"1")):
        response = client.post(
            "/files/upload",
            headers=headers,
            files={"file": (filename, data, "application/octet-stream")},
        )
        assert response.status_code == 200

    first_page = client.get("/files/?page=1&page_size=2&sort_by=filename&sort_order=asc", headers=headers)
    assert first_page.status_code == 200
    assert [item["filename"] for item in first_page.json()["items"]] == ["Alpha.txt", "beta.txt"]
    assert first_page.json()["total"] == 3
    assert first_page.json()["total_pages"] == 2

    search = client.get("/files/?search=ALPHA", headers=headers)
    assert [item["filename"] for item in search.json()["items"]] == ["Alpha.txt"]
    assert client.get("/files/?sort_by=object_key", headers=headers).status_code == 422
    assert client.get("/files/?page_size=101", headers=headers).status_code == 422


def test_share_link_redirect_counts_and_enforces_download_limit(client: TestClient) -> None:
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    uploaded = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("shared document.txt", b"shared", "text/plain")},
    )
    file_id = uploaded.json()["id"]

    created = client.post(
        f"/files/{file_id}/share",
        headers=headers,
        json={"expires_in_hours": 1, "max_downloads": 1},
    )
    assert created.status_code == 201, created.text
    share = created.json()
    token_value = share["share_url"].rsplit("/", 1)[1]
    assert token_value

    downloaded = client.get(f"/share/{token_value}", follow_redirects=False)
    assert downloaded.status_code == 307
    assert downloaded.headers["location"].startswith("https://storage.test/")
    assert client.get(f"/share/{token_value}").status_code == 410
    listed = client.get(f"/files/{file_id}/shares", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["download_count"] == 1


def test_share_links_can_be_revoked_and_are_owner_scoped(client: TestClient) -> None:
    register(client, "alice@example.com")
    register(client, "bob@example.com")
    alice_token = login(client, "alice@example.com")
    bob_token = login(client, "bob@example.com")
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    bob_headers = {"Authorization": f"Bearer {bob_token}"}
    file_id = client.post(
        "/files/upload",
        headers=alice_headers,
        files={"file": ("share.txt", b"content", "text/plain")},
    ).json()["id"]
    share = client.post(f"/files/{file_id}/share", headers=alice_headers, json={}).json()
    share_token = share["share_url"].rsplit("/", 1)[1]

    assert client.delete(
        f"/files/{file_id}/share/{share['id']}", headers=bob_headers
    ).status_code == 404
    assert client.delete(
        f"/files/{file_id}/share/{share['id']}", headers=alice_headers
    ).status_code == 200
    assert client.get(f"/share/{share_token}").status_code == 404


def test_expired_share_link_returns_gone(client: TestClient, monkeypatch) -> None:
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    file_id = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("expire.txt", b"content", "text/plain")},
    ).json()["id"]
    share = client.post(f"/files/{file_id}/share", headers=headers, json={}).json()
    share_token = share["share_url"].rsplit("/", 1)[1]

    real_datetime = share_service_module.datetime

    class FutureDatetime:
        @classmethod
        def now(cls, tz=None):
            return real_datetime.now(tz) + share_service_module.timedelta(days=2)

    monkeypatch.setattr(share_service_module, "datetime", FutureDatetime)
    assert client.get(f"/share/{share_token}").status_code == 410


def test_login_rate_limit_returns_retry_after(client: TestClient) -> None:
    for attempt in range(11):
        response = client.post(
            "/auth/login",
            data={"username": "no-user@example.com", "password": "invalid-password"},
        )
        if attempt < 10:
            assert response.status_code == 401
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0


def test_rate_limit_fails_closed_when_redis_is_unavailable(client: TestClient) -> None:
    from redis.exceptions import ConnectionError as RedisConnectionError

    class BrokenRedis:
        def eval(self, *_args):
            raise RedisConnectionError("offline")

    client.app.dependency_overrides[get_rate_limiter] = lambda: RateLimiter(BrokenRedis())
    response = client.post(
        "/auth/login",
        data={"username": "no-user@example.com", "password": "invalid-password"},
    )
    assert response.status_code == 503


def test_upload_initiation_rate_limit_returns_429(client: TestClient) -> None:
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    for attempt in range(11):
        response = client.post(
            "/uploads/initiate",
            headers=headers,
            json={"filename": f"file-{attempt}.bin", "total_chunks": 1},
        )
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_chunk_upload_rate_limit_returns_429(client: TestClient, monkeypatch) -> None:
    import routers.uploads as uploads_module

    monkeypatch.setattr(uploads_module, "chunk_rate_limit", 1)
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    initiated = client.post(
        "/uploads/initiate",
        headers=headers,
        json={"filename": "two-chunks.bin", "total_chunks": 2},
    )
    upload_id = initiated.json()["upload_id"]
    first = client.post(
        f"/uploads/{upload_id}/chunks/1",
        headers=headers,
        files={"file": ("chunk", b"first", "application/octet-stream")},
    )
    second = client.post(
        f"/uploads/{upload_id}/chunks/2",
        headers=headers,
        files={"file": ("chunk", b"second", "application/octet-stream")},
    )
    assert first.status_code == 200
    assert second.status_code == 429


def test_download_reports_object_storage_unavailable(
    client: TestClient, storage: MemoryStorage
) -> None:
    register(client, "alice@example.com")
    token = login(client, "alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    file_id = client.post(
        "/files/upload",
        headers=headers,
        files={"file": ("unavailable.txt", b"content", "text/plain")},
    ).json()["id"]

    def fail_to_sign(*_args, **_kwargs):
        raise StorageError("offline")

    storage.generate_download_url = fail_to_sign
    response = client.get(f"/files/{file_id}/download", headers=headers)
    assert response.status_code == 503
    assert response.json()["detail"] == "Object storage is unavailable"


def test_presigned_download_uses_original_utf8_filename() -> None:
    from datetime import timedelta

    from storage.minio_storage import MinioStorage

    class PresignClient:
        def presigned_get_object(self, **kwargs):
            self.arguments = kwargs
            return "https://storage.test/download"

    storage = MinioStorage.__new__(MinioStorage)
    storage.bucket = "filevault"
    storage.presign_client = PresignClient()
    url = storage.generate_download_url(
        "objects/document",
        timedelta(minutes=5),
        filename="café notes.pdf",
    )

    assert url == "https://storage.test/download"
    assert storage.presign_client.arguments["response_headers"] == {
        "response-content-disposition": "attachment; filename*=UTF-8''caf%C3%A9%20notes.pdf"
    }
