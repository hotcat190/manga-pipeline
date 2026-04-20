import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class WordChunk(BaseModel):
    word: str
    romaji: str
    type: str
    meaning: str

class TranslationResult(BaseModel):
    original_text: str
    full_translation: str
    chunks: List[WordChunk]

class MangaTranslator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

    def translate_batch(self, metadata: List[Dict], target_lang: str) -> tuple[Dict, Dict]:
        page_context = " ".join([item["original_text"] for item in metadata])
        
        original_data = []
        translation_data = []

        for item in metadata:
            text = item["original_text"]
            if not text.strip():
                continue

            prompt = f"""
            Translate this manga text to {target_lang}.
            Context: "{page_context}"
            Text to translate: "{text}"
            """
            
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=TranslationResult,
                        temperature=0.4
                    )
                )
                result = json.loads(response.text)
                
                original_chunks = []
                chunk_meanings = []
                
                for idx, chunk in enumerate(result["chunks"]):
                    chunk_id = f"c{idx + 1}"
                    original_chunks.append({
                        "chunk_id": chunk_id,
                        "word": chunk["word"],
                        "romaji": chunk["romaji"],
                        "type": chunk["type"]
                    })
                    chunk_meanings.append({chunk_id: chunk["meaning"]})
                
                original_data.append({
                    "id": item["id"],
                    "box": item["box"],
                    "original_text": item["original_text"],
                    "chunks": original_chunks
                })
                
                translation_data.append({
                    "id": item["id"],
                    "full_translation": result["full_translation"],
                    "chunk_meanings": chunk_meanings
                })
                
            except Exception:
                pass
                
        return original_data, translation_data