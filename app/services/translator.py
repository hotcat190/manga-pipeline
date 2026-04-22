import json
import google.generativeai as genai
from pydantic import BaseModel
from typing import List, Dict
from app.core.utils import get_full_lang_name
from app.services.nlp import NLPAnalyzer, DictionaryLookup
from app.core.config import settings

class TranslatedItem(BaseModel):
    id: int
    full_translation: str

class BatchTranslationResult(BaseModel):
    translations: List[TranslatedItem]

class MangaTranslator:
    def __init__(self, api_key: str = None):
        api_key = api_key or settings.GEMINI_API_KEY
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        self.nlp = NLPAnalyzer()
        self.dictionary = DictionaryLookup()

    def translate_batch(self, metadata: List[Dict], source_lang: str, target_lang: str) -> tuple[List[Dict], List[Dict]]:
        print("Bắt đầu pipeline dịch thuật")
        full_source_lang = get_full_lang_name(source_lang)
        full_target_lang = get_full_lang_name(target_lang)
        
        original_data = []
        translation_data = []
        valid_items = [item for item in metadata if item["original_text"].strip()]

        print("2. Bắt đầu dịch thuật chuyên sâu (Tap-to-Translate Pipeline)...\n")
        for item in valid_items:
            text = item["original_text"]
            chunks = self.nlp.analyze(text, source_lang)

            original_chunks = []
            chunk_meanings = []
            
            for idx, chunk in enumerate(chunks):
                chunk_id = f"c{idx + 1}"
                original_chunks.append({
                    "chunk_id": chunk_id,
                    "word": chunk["word"],
                    "romaji": chunk["romaji"],
                    "type": chunk["type"]
                })
                meaning = self.dictionary.get_meaning(chunk["word"], source_lang, target_lang)
                chunk_meanings.append({chunk_id: meaning})
            
            original_data.append({
                "id": item["id"],
                "box": item["box"],
                "original_text": text,
                "chunks": original_chunks
            })
            
            translation_data.append({
                "id": item["id"],
                "full_translation": "",
                "chunk_meanings": chunk_meanings
            })

        lines_to_translate = "\n".join([f"[{item['id']}] {item['original_text']}" for item in valid_items])
        prompt = f"""
        You are an expert manga/webtoon translator. Translate the following {full_source_lang} dialogue lines into highly idiomatic {full_target_lang}.
        Context is provided by all the lines together. Match the character's tone and infer missing subjects naturally.
        
        INPUT TEXT:
        {lines_to_translate}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=BatchTranslationResult,
                    temperature=1
                )
            )
            result = json.loads(response.text)
            
            translation_map = {t["id"]: t["full_translation"] for t in result.get("translations", [])}
            for t_data in translation_data:
                t_data["full_translation"] = translation_map.get(t_data["id"], "")
                
        except Exception:
            pass
                
        return original_data, translation_data