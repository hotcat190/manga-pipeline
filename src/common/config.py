from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    
    # Model Paths
    PANEL_MODEL_PATH: str = Field("models/yolov12x_panels.pt", env="PANEL_MODEL_PATH")
    TEXT_DETECTION_MODEL_PATH: str = Field("models/comictextdetector.pt", env="TEXT_DETECTION_MODEL_PATH")
    
    # Storage Config
    DEFAULT_BUCKET_NAME: str = Field("comic", env="DEFAULT_BUCKET_NAME")
    LOCAL_OUTPUT_DIR: str = Field("local_output", env="LOCAL_OUTPUT_DIR")
    MINIO_ENDPOINT: str = Field("http://minio:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field("admin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field("password123", env="MINIO_SECRET_KEY")
    MINIO_PUBLIC_BASE_URL: str = Field("http://localhost:9000/comic", env="MINIO_PUBLIC_BASE_URL")
    
    # AI Model Config
    GEMINI_MODEL_NAME: str = Field("gemini-3.1-flash-lite-preview", env="GEMINI_MODEL_NAME")
    
    # App Config
    DEBUG: bool = Field(False, env="DEBUG")
    
    model_config = SettingsConfigDict(
        env_file=".env.local.test",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
