import pytest
from model import get_model


class TestModel:
    def test_model_loaded(self):
        model = get_model()
        assert model is not None

    def test_model_predict(self):
        model = get_model()
        result = model.predict(["test article content"])
        assert result is not None
        assert len(result) == 1
