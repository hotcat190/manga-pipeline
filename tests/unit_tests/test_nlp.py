import pytest
from app.services.nlp import NLPAnalyzer, DictionaryLookup

@pytest.fixture
def nlp_analyzer():
    return NLPAnalyzer()

@pytest.fixture
def dictionary_lookup():
    return DictionaryLookup()

def test_analyze_jp(nlp_analyzer):
    result = nlp_analyzer.analyze("こんにちは", "ja")
    assert len(result) == 1
    assert result[0]["word"] == "こんにちは"
    assert result[0]["romaji"] == "konnichiwa"
    assert result[0]["type"] == "interjection"

def test_analyze_kr(nlp_analyzer):
    result = nlp_analyzer.analyze("안녕하세요", "ko")
    assert len(result) == 1
    assert result[0]["word"] == "안녕하세요"
    assert result[0]["romaji"] == "romaja_mock"
    assert result[0]["type"] == "noun"

def test_analyze_cn(nlp_analyzer):
    result = nlp_analyzer.analyze("你好", "zh")
    assert len(result) == 1
    assert result[0]["word"] == "你好"
    assert result[0]["romaji"] == "pinyin_mock"
    assert result[0]["type"] == "noun"

def test_analyze_unsupported_lang(nlp_analyzer):
    result = nlp_analyzer.analyze("hello", "en")
    assert result == []

def test_dictionary_get_meaning(dictionary_lookup):
    assert dictionary_lookup.get_meaning("こんにちは", "ja", "en") == "mock_meaning_in_en"
    assert dictionary_lookup.get_meaning("こんにちは", "ja", "vi") == "mock_meaning_in_vi"