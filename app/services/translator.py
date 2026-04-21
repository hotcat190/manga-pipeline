import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.core.utils import get_full_lang_name, get_few_shot_example

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

    def translate_batch(self, metadata: List[Dict], source_lang: str, target_lang: str) -> tuple[Dict, Dict]:
        print("Bắt đầu pipeline dịch thuật")
        print("1. Đang tổng hợp ngữ cảnh toàn trang...")

        page_context = "\n".join([item["original_text"] for item in metadata])
        full_source_lang = get_full_lang_name(source_lang)
        full_target_lang = get_full_lang_name(target_lang)
        few_shot_example = get_few_shot_example(target_lang)

        print(f"Ngữ cảnh:\n{page_context}")
        
        original_data = []
        translation_data = []

        print("2. Bắt đầu dịch thuật chuyên sâu (Tap-to-Translate Pipeline)...\n")
        for item in metadata:
            text = item["original_text"]
            if not text.strip():
                continue

            print(f"Đang xử lý: {text}")

            prompt = f"""
            You are an expert Manga/Webtoon translator and a {full_source_lang} linguistics tutor. 
            Your task is to translate {full_source_lang} dialogue into {full_target_lang} and deeply analyze its grammatical structure for language learners.

            ### CORE INSTRUCTIONS:
            1. **Localization & Accuracy**: The `full_translation` MUST be highly idiomatic, matching the character's tone in the [PAGE CONTEXT]. Do not output literal translations.
            2. **Context Resolution**: {full_source_lang} frequently omits subjects. Use the [PAGE CONTEXT] to infer hidden pronouns, gender, and relationships.
            3. **Strict Semantic Chunking**: 
            - Break the text into granular, meaningful chunks.
            - **ZERO-TOLERANCE RULE**: The exact string concatenation of all `word` values MUST perfectly match the [ORIGINAL TEXT]. Include all punctuation marks (..., !, ?, ~) as separate chunks of type "punctuation".
            4. **Transliteration Accuracy**: The `romaji` field MUST be the correct romanization (e.g., Romaji for Japanese, Pinyin for Chinese, Romaja for Korean) of the `word`.
            5. **POS Tagging**: The `type` field MUST strictly be one of: "noun", "verb", "adjective", "adverb", "particle", "pronoun", "interjection", "onomatopoeia", "punctuation", "other".
            6. **Target Language Meaning**: The `meaning` field MUST explain the word's specific contextual definition IN {full_target_lang}.

            ### FEW-SHOT EXAMPLE FOR CHUNKING:
            If the source text is: "俺は...絶対に諦めない！"
            Your chunks should logically be:
            {few_shot_example}

            ### INPUT DATA:
            [PAGE CONTEXT]
            "{page_context}"

            [ORIGINAL TEXT]
            "{text}"
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
                print(f"response: {response}")
                result = json.loads(response.text)
                print(f"result: {result}")
                
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
                
            except Exception as e:
                print(f"Lỗi khi dịch câu '{text}': {e}")
                pass
                
        return original_data, translation_data