class StorageService:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def upload_image(self, image, path: str) -> str:
        return f"https://s3.yourdomain.com/{self.bucket_name}/{path}"

    def upload_json(self, data: dict, path: str) -> str:
        return f"https://s3.yourdomain.com/{self.bucket_name}/{path}"