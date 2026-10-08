from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.files import public_share_router, router as file_router
from routers.uploads import router as uploads_router


app = FastAPI(
    title="Filevault API",
    summary="Self-hosted file storage with chunked uploads and expiring shares.",
    description=(
        "Filevault stores file metadata in PostgreSQL and file contents in "
        "S3-compatible object storage. Private file operations are scoped to "
        "the authenticated user; public share links support expiration and "
        "download limits."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Auth", "description": "Create an account and obtain a bearer token."},
        {"name": "Files", "description": "List, upload, download, and delete your files."},
        {"name": "Uploads", "description": "Upload large files in numbered chunks."},
        {"name": "Sharing", "description": "Create expiring public links to download files."},
    ],
)


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(file_router)
app.include_router(uploads_router)
app.include_router(public_share_router)
