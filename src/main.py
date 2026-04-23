import logging
from typing import Dict, Optional
from src.engines.factory import OcrFactory
from src.services.translator import MangaTranslator
from src.services.storage import BaseStorageService, StorageService
from src.common.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MangaPipeline:
    def __init__(self, storage_service: Optional[BaseStorageService] = None):
        self.engines = {
            'manga': OcrFactory.get_engine('manga'),
            'webtoon': OcrFactory.get_engine('webtoon')
        }
        self.translator = MangaTranslator()
        self.storage = storage_service or StorageService(bucket_name=settings.DEFAULT_BUCKET_NAME)

    def process_job(self, job_payload: Dict) -> Dict:
        job_id = job_payload.get("job_id")
        page_id = job_payload.get("page_id")
        comic_type = job_payload.get("comic_type", "manga")
        
        logger.info(f"Processing job {job_id} (Type: {comic_type}, Page: {page_id})")

        try:
            # 1. Get Engine
            engine = self.engines.get(comic_type)
            if not engine:
                raise ValueError(f"Unsupported comic type: {comic_type}")

            # 2. Process Image (OCR + Inpainting)
            image_path = job_payload.get("image_path")
            if not image_path:
                raise ValueError("Missing 'image_path' in payload")

            cleaned_img, metadata = engine.process(image_path)
            
            # 3. Upload Cleaned Image
            img_url = self.storage.upload_image(cleaned_img, f"processed/{job_id}/clean.jpg")

            # 4. (Optional) Skip translation
            skip_translate = job_payload.get("skip_translate", False)
            if skip_translate:
                logger.info(f"Job {job_id}: skip_translate=True, skipping translation step")
                return {
                    "job_id": job_id,
                    "status": "COMPLETED",
                    "result": {
                        "inpainted_image_url": img_url,
                        "metadata": None
                    }
                }

            # 5. Handle Translations
            final_translations = {}
            original_metadata_full = {
                "page_id": page_id,
                "bubbles": []
            }

            source_lang = job_payload.get("source_lang", "ja")
            target_langs = job_payload.get("target_langs", ["vi"])

            for lang in target_langs:
                orig_data, trans_data = self.translator.translate_batch(
                    metadata,
                    source_lang=source_lang,
                    target_lang=lang
                )

                if not original_metadata_full["bubbles"]:
                    original_metadata_full["bubbles"] = orig_data

                trans_metadata_full = {
                    "page_id": page_id,
                    "bubbles": trans_data
                }

                trans_url = self.storage.upload_json(
                    trans_metadata_full,
                    f"metadata/{job_id}/trans_{lang}.json"
                )
                final_translations[lang] = trans_url

            # 6. Upload Original Metadata
            orig_url = self.storage.upload_json(
                original_metadata_full,
                f"metadata/{job_id}/original.json"
            )
            
            logger.info(f"Job {job_id} completed successfully")
            
            return {
                "job_id": job_id,
                "status": "COMPLETED",
                "result": {
                    "inpainted_image_url": img_url,
                    "metadata": {
                        "original_url": orig_url,
                        "translations": final_translations
                    }
                }
            }

        except Exception as e:
            logger.exception(f"Failed to process job {job_id}")
            return {
                "job_id": job_id,
                "status": "FAILED",
                "error": str(e)
            }

def process_job(job_payload: Dict) -> Dict:
    """Wrapper function to maintain backward compatibility if needed."""
    return pipeline.process_job(job_payload)