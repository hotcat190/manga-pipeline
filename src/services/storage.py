import os
import json
from abc import ABC, abstractmethod

class BaseStorageService(ABC):
    @abstractmethod
    def upload_image(self, image, path: str) -> str: pass
    
    @abstractmethod
    def upload_json(self, data: dict, path: str) -> str: pass

class StorageService(BaseStorageService):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def upload_image(self, image, path: str) -> str:
        return f"https://s3.yourdomain.com/{self.bucket_name}/{path}"

    def upload_json(self, data: dict, path: str) -> str:
        return f"https://s3.yourdomain.com/{self.bucket_name}/{path}"

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