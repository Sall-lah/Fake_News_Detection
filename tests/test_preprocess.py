import pytest
from preprocess import clean_text


class TestPreprocess:
    def test_clean_text_with_title_and_text(self):
        result = clean_text("Test Title", "This is a test article")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_clean_text_removes_punctuation(self):
        result = clean_text("", "Hello, world! This is a test.")
        assert "," not in result
        assert "!" not in result

    def test_clean_text_lowercase(self):
        result = clean_text("", "HELLO WORLD")
        assert result == result.lower()

    def test_clean_text_empty_input(self):
        result = clean_text("", "")
        assert result == ""
