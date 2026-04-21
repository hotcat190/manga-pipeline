from typing import List, Dict
from sudachipy import tokenizer
from sudachipy import dictionary
import pykakasi

class NLPAnalyzer:
    def __init__(self):
        self.su_dict = dictionary.Dictionary(dict="full")
        self.su_obj = self.su_dict.create()
        self.mode = tokenizer.Tokenizer.SplitMode.A

        self.jp_pos_map = {
            "名詞": "noun",
            "代名詞": "pronoun",
            "動詞": "verb",
            "形容詞": "adjective",
            "形状詞": "adjective",
            "副詞": "adverb",
            "助詞": "particle",
            "助動詞": "verb",
            "感動詞": "interjection",
            "記号": "punctuation",
            "補助記号": "punctuation",
            "連体詞": "other",
            "接続詞": "other",
            "接頭辞": "other",
            "接尾辞": "other"
        }

        self.kakasi = pykakasi.kakasi()

    def analyze(self, text: str, lang: str) -> List[Dict]:
        if lang == 'ja':
            return self._analyze_jp(text)
        elif lang == 'ko':
            return self._analyze_kr(text)
        elif lang == 'zh':
            return self._analyze_cn(text)
        return []

    def _get_phonetic_romaji_jp(self, token) -> str:
        surface = token.surface()
        pos = token.part_of_speech()[0]
        
        if pos == "助詞":
            if surface == "は": return "wa"
            if surface == "へ": return "e"
            if surface == "を": return "o"
            
        if pos == "感動詞":
            if surface == "こんにちは": return "konnichiwa"
            if surface == "こんばんは": return "konbanwa"
            
        reading = token.reading_form()
        kks_result = self.kakasi.convert(reading)
        return "".join([item['hepburn'] for item in kks_result])

    def _analyze_jp(self, text: str) -> List[Dict]:
        result = []

        tokens = self.su_obj.tokenize(text, self.mode)
        
        for token in tokens:
            pos_tag = token.part_of_speech()[0]
            mapped_pos = self.jp_pos_map.get(pos_tag, "other")
        
            result.append({
                "word": token.surface(),
                "romaji": self._get_phonetic_romaji_jp(token),
                "type": mapped_pos
            })
        return result

    def _analyze_kr(self, text: str) -> List[Dict]:
        return [{"word": text, "romaji": "romaja_mock", "type": "noun"}]

    def _analyze_cn(self, text: str) -> List[Dict]:
        return [{"word": text, "romaji": "pinyin_mock", "type": "noun"}]

class DictionaryLookup:
    def get_meaning(self, word: str, source_lang: str, target_lang: str) -> str:
        return f"mock_meaning_in_{target_lang}"