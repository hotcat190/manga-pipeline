import os
import json
import io
from abc import ABC, abstractmethod
from minio import Minio
from src.common.config import settings

class BaseStorageService(ABC):
    @abstractmethod
    def upload_image(self, image, path: str) -> str: pass
    
    @abstractmethod
    def upload_json(self, data: dict, path: str) -> str: pass

class MinioStorageService(BaseStorageService):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.public_base_url = settings.MINIO_PUBLIC_BASE_URL.rstrip('/')
        
        endpoint = settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
        
        self.client = Minio(
            endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_ENDPOINT.startswith("https")
        )
        
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_image(self, image, path: str) -> str:
        img_byte_arr = io.BytesIO()
        format_type = "PNG" if path.lower().endswith(".png") else "JPEG"
        image.save(img_byte_arr, format=format_type)
        img_byte_arr.seek(0)
        
        self.client.put_object(
            self.bucket_name,
            path,
            img_byte_arr,
            length=img_byte_arr.getbuffer().nbytes,
            content_type=f"image/{format_type.lower()}"
        )
        return f"{self.public_base_url}/{path}"

    def upload_json(self, data: dict, path: str) -> str:
        json_str = json.dumps(data, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        byte_stream = io.BytesIO(json_bytes)
        
        self.client.put_object(
            self.bucket_name,
            path,
            byte_stream,
            length=len(json_bytes),
            content_type="application/json"
        )
        return f"{self.public_base_url}/{path}"


class LocalStorageService(BaseStorageService):
    def __init__(self, output_dir: str = "local_output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def upload_image(self, image, path: str) -> str:
        local_path = os.path.join(self.output_dir, os.path.basename(path))
        image.save(local_path)
        return local_path
        
    def upload_json(self, data: dict, path: str) -> str:
        local_path = os.path.join(self.output_dir, os.path.basename(path))
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return local_path