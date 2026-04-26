"""Tests for ModelsApp data helpers.
b17: WDASH  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
import json
from grove.apps.models import list_models, get_active_model, set_active_model


def _mock_ollama(names):
    data = json.dumps({"models": [{"name": n} for n in names]}).encode()
    resp = MagicMock()
    resp.read.return_value = data
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_list_models_returns_names():
    with patch("urllib.request.urlopen", return_value=_mock_ollama(["yggdrasil:v9", "qwen2.5:3b"])):
        models = list_models()
    assert "yggdrasil:v9" in models
    assert "qwen2.5:3b" in models


def test_list_models_empty_on_error():
    with patch("urllib.request.urlopen", side_effect=Exception("refused")):
        models = list_models()
    assert models == []


def test_set_get_active_model():
    with patch("soil.put") as mock_put, \
         patch("soil.get", return_value={"value": "qwen2.5:3b"}):
        set_active_model("qwen2.5:3b")
        mock_put.assert_called_once_with(
            "willow-dashboard/config", "active_model", {"value": "qwen2.5:3b"})
        model = get_active_model()
    assert model == "qwen2.5:3b"


def test_get_active_model_default():
    with patch("soil.get", return_value=None):
        model = get_active_model()
    assert model == ""
