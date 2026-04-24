import json
import logging
import google.generativeai as genai
from pydantic import BaseModel
from typing import List, Dict, Tuple
from PIL import Image
from src.common.utils import get_full_lang_name
from src.common.config import settings
from src.services.prompts import TRANSLATION_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class ChunkItem(BaseModel):
    chunk_id: str
    word: str
    romaji: str
    type: str
    meaning_in_context: str

class TranslatedItem(BaseModel):
    id: int
    full_translation: str
    chunks: List[ChunkItem]

class BatchTranslationResult(BaseModel):
    translations: List[TranslatedItem]

class MangaTranslator:
    def __init__(self, api_key: str = None):
        api_key = api_key or settings.GEMINI_API_KEY
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)

    def translate_batch(self, metadata: List[Dict], som_image: Image.Image, source_lang: str, target_lang: str) -> Tuple[List[Dict], List[Dict]]:
        logger.info(f"Starting translation pipeline: {source_lang} -> {target_lang}")
        full_source_lang = get_full_lang_name(source_lang)
        full_target_lang = get_full_lang_name(target_lang)
        
        original_data = []
        translation_data = []
        valid_items = [item for item in metadata if item["original_text"].strip()]

        for item in valid_items:            
            original_data.append({
                "id": item["id"],
                "box": item["box"],
                "original_text": item["original_text"]
            })
            
            translation_data.append({
                "id": item["id"]
            })

        lines_to_translate = "\n".join([f"[{item['id']}] {item['original_text']}" for item in valid_items])
        prompt = TRANSLATION_PROMPT_TEMPLATE.format(
            source_lang=full_source_lang,
            target_lang=full_target_lang,
            input_text=lines_to_translate
        )
        
        try:
            response = self.model.generate_content(
                [som_image, prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=BatchTranslationResult,
                    temperature=1,
                    top_p=0.95,
                    top_k=64,
                )
            )
            result = json.loads(response.text)          
            
            translation_map = {t["id"]: t for t in result.get("translations", [])}

            for o_data in original_data:
                llm_result = translation_map.get(o_data["id"])
                if llm_result:
                    o_data["chunks"] = [{
                        "chunk_id": c["chunk_id"],
                        "word": c["word"],
                        "romaji": c["romaji"],
                        "type": c["type"]
                    } for c in llm_result.get("chunks", [])]

            for t_data in translation_data:
                llm_result = translation_map.get(t_data["id"])
                if llm_result:
                    t_data["full_translation"] = llm_result.get("full_translation", "")
                    t_data["chunk_meanings"] = [{c["chunk_id"]: c["meaning_in_context"]} for c in llm_result.get("chunks", [])]
                
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            for t_data in translation_data:
                t_data["full_translation"] = t_data.get("full_translation", "[Translation Error]")
                t_data["chunk_meanings"] = t_data.get("chunk_meanings", [])
                
        return original_data, translation_data