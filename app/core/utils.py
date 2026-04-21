lang_code_map = {
    'vi': 'Vietnamese',
    'en': 'English',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'th': 'Thai',
    'id': 'Indonesian'
}

def get_full_lang_name(lang_code: str) -> str:
    return lang_code_map.get(lang_code.lower(), lang_code)

def get_few_shot_example(lang_code: str) -> str:
    lang = lang_code.lower()
    if lang == 'vi':
        return """
        - "俺" (noun: tôi/tao)
        - "は" (particle: trợ từ chủ đề)
        - "..." (punctuation)
        - "絶対に" (adverb: tuyệt đối/nhất định)
        - "諦めない" (verb: không bỏ cuộc)
        - "！" (punctuation)
        """
    return """
        - "俺" (noun: I)
        - "は" (particle: topic marker)
        - "..." (punctuation)
        - "絶対に" (adverb: absolutely)
        - "諦めない" (verb: will not give up)
        - "！" (punctuation)
        """