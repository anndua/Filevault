import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL= os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)

endpoint = os.getenv("MINIO_ENDPOINT")
public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", endpoint)
minio_region = os.getenv("MINIO_REGION", "us-east-1")
access_key = os.getenv("MINIO_ACCESS_KEY")
secret_key = os.getenv("MINIO_SECRET_KEY")
bucket = os.getenv("MINIO_BUCKET")
secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
login_rate_limit = int(os.getenv("LOGIN_RATE_LIMIT", "10"))
upload_rate_limit = int(os.getenv("UPLOAD_RATE_LIMIT", "10"))
chunk_rate_limit = int(os.getenv("CHUNK_RATE_LIMIT", "120"))
share_public_base_url = os.getenv("SHARE_PUBLIC_BASE_URL", "").rstrip("/")