from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GEMINI_API_KEY: str

    PANEL_MODEL_PATH: str = "models/yolov12x_panels.pt"
    TEXT_DETECTION_MODEL_PATH: str = "models/comictextdetector.pt"

    DEFAULT_BUCKET_NAME: str = "comic"
    LOCAL_OUTPUT_DIR: str = "local_output"
    MINIO_ENDPOINT: str = "http://minio:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "password123"
    MINIO_PUBLIC_BASE_URL: str = "http://localhost:9000/comic"

    GEMINI_MODEL_NAME: str = "gemini-3.1-flash-lite"

    DEBUG: bool = False

settings = Settings()
