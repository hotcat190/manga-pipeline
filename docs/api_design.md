# API Design

## Request Schema

```json
{
    "job_id": "job_987654321",
    "page_id": "page_01",
    "chapter_id": "chapter_05",
    "image_url": "https://s3.yourdomain.com/raw/manga_1/ch_5/page_01.jpg",
    "source_lang": "ja",
    "target_langs": [
        "vi",
        "en"
    ],
    "webhook_url": "https://api.yourdomain.com/internal/pipeline-callback"
}
```

## Response Schema

### Successful

```json
{
    "job_id": "job_987654321",
    "status": "COMPLETED",
    "page_id": "page_01",
    "chapter_id": "chapter_05",
    "result": {
        "inpainted_image_url": "https://s3.yourdomain.com/processed/manga_1/ch_5/page_01_cleaned.jpg",
        "metadata": {
            "original_url": "https://s3.yourdomain.com/metadata/manga_1/ch_5/page_01_original.json",
            "translations": {
                "vi": "https://s3.yourdomain.com/metadata/manga_1/ch_5/page_01_vi.json",
                "en": "https://s3.yourdomain.com/metadata/manga_1/ch_5/page_01_en.json"
            }
        }
    }
}
```

### Failure

```json
{
    "job_id": "job_987654321",
    "status": "FAILED",
    "page_id": "page_01",
    "chapter_id": "chapter_05",
    "error_message": "Job failed due to exceeeded LLM quota"
}
```
