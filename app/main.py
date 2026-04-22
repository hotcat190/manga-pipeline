from typing import Dict
from app.engines.factory import OcrFactory
from app.services.translator import MangaTranslator
from app.services.storage import BaseStorageService, StorageService
from app.core.config import settings

ocr_engines = {
    'manga': None,
    'webtoon': None
}

def init_engines():
    ocr_engines['manga'] = OcrFactory.get_engine('manga')
    ocr_engines['webtoon'] = OcrFactory.get_engine('webtoon')

def process_job(job_payload: Dict, storage: BaseStorageService = None) -> Dict:
    comic_type = job_payload.get("comic_type", "manga")
    engine = ocr_engines.get(comic_type)
    
    translator = MangaTranslator()
    
    if storage is None:
        storage = StorageService(bucket_name=job_payload.get("bucket_name", settings.DEFAULT_BUCKET_NAME))
    
    image_path = job_payload.get("image_path", "/tmp/downloaded_image.jpg")
    
    cleaned_img, metadata = engine.process(image_path)
    
    img_url = storage.upload_image(cleaned_img, f"processed/{job_payload['job_id']}/clean.jpg")
    
    final_translations = {}
    original_metadata_full = {
        "page_id": job_payload["page_id"],
        "bubbles": []
    }
    
    for lang in job_payload["target_langs"]:
        orig_data, trans_data = translator.translate_batch(metadata, source_lang=job_payload["source_lang"], target_lang=lang)
        
        if not original_metadata_full["bubbles"]:
            original_metadata_full["bubbles"] = orig_data
            
        trans_metadata_full = {
            "page_id": job_payload["page_id"],
            "bubbles": trans_data
        }
        
        trans_url = storage.upload_json(trans_metadata_full, f"metadata/{job_payload['job_id']}/trans_{lang}.json")
        final_translations[lang] = trans_url
        
    orig_url = storage.upload_json(original_metadata_full, f"metadata/{job_payload['job_id']}/original.json")
    
    return {
        "job_id": job_payload["job_id"],
        "status": "COMPLETED",
        "result": {
            "inpainted_image_url": img_url,
            "metadata": {
                "original_url": orig_url,
                "translations": final_translations
            }
        }
    }