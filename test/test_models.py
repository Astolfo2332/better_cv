"""
Tests para los modelos LLM (base_model, openai_model, google_gen)
"""
import pytest
from unittest.mock import Mock, patch

from src.application.models.base_model import LlmBaseModel
from src.application.models.openai_model import OpenAIModel
from src.application.models.google_gen import GoogleGenModel


class TestLlmBaseModel:
    def test_initial_client_is_none(self):
        model = LlmBaseModel()

        assert model.client is None

    def test_initial_models_is_empty_list(self):
        model = LlmBaseModel()

        assert model.models == []

    def test_get_available_models_returns_models_list(self):
        model = LlmBaseModel()
        model.models = ["model1", "model2"]

        result = model.get_available_models()

        assert result == ["model1", "model2"]

    def test_get_model_raises_error_when_not_started(self):
        model = LlmBaseModel()

        with pytest.raises(ValueError, match="Model session has not been started"):
            model.get_model()

    def test_get_model_returns_client_when_started(self):
        model = LlmBaseModel()
        model.client = Mock()

        result = model.get_model()

        assert result == model.client

    def test_start_session_raises_not_implemented(self):
        model = LlmBaseModel()

        with pytest.raises(NotImplementedError):
            model.start_session("model_name")


class TestOpenAIModel:
    def test_inherits_from_base_model(self):
        model = OpenAIModel()

        assert isinstance(model, LlmBaseModel)

    def test_initial_client_is_none(self):
        model = OpenAIModel()

        assert model.client is None

    def test_has_predefined_models(self):
        model = OpenAIModel()

        assert len(model.models) > 0
        assert "gpt-5.2" in model.models

    def test_get_available_models_returns_supported_models(self):
        model = OpenAIModel()

        result = model.get_available_models()

        assert "gpt-5.2" in result
        assert "gpt-4.1" in result

    @patch("src.application.models.openai_model.ChatOpenAI")
    def test_start_session_creates_client(self, mock_chat):
        model = OpenAIModel()

        model.start_session("gpt-5.2")

        mock_chat.assert_called_once()
        assert model.client is not None

    @patch("src.application.models.openai_model.ChatOpenAI")
    def test_start_session_uses_correct_model_name(self, mock_chat):
        model = OpenAIModel()

        model.start_session("gpt-4.1")

        mock_chat.assert_called_with(model="gpt-4.1", reasoning_effort="medium")

    def test_start_session_raises_error_for_invalid_model(self):
        model = OpenAIModel()

        with pytest.raises(ValueError, match="is not supported"):
            model.start_session("invalid-model")

    @patch("src.application.models.openai_model.ChatOpenAI")
    def test_start_session_with_custom_reasoning(self, mock_chat):
        model = OpenAIModel()

        model.start_session("gpt-5.2", reasoning="high")

        mock_chat.assert_called_with(model="gpt-5.2", reasoning_effort="high")

    @patch("src.application.models.openai_model.ChatOpenAI")
    def test_get_model_after_session_started(self, mock_chat):
        model = OpenAIModel()
        mock_chat.return_value = Mock()

        model.start_session("gpt-5.2")
        result = model.get_model()

        assert result == mock_chat.return_value


class TestGoogleGenModel:
    def test_inherits_from_base_model(self):
        model = GoogleGenModel()

        assert isinstance(model, LlmBaseModel)

    def test_initial_client_is_none(self):
        model = GoogleGenModel()

        assert model.client is None

    def test_has_predefined_models(self):
        model = GoogleGenModel()

        assert len(model.models) > 0
        assert "gemini-3-flash-preview" in model.models

    def test_get_available_models_returns_supported_models(self):
        model = GoogleGenModel()

        result = model.get_available_models()

        assert "gemini-3-flash-preview" in result
        assert "gemini-2.5-pro" in result

    @patch("src.application.models.google_gen.ChatGoogleGenerativeAI")
    def test_start_session_creates_client(self, mock_chat):
        model = GoogleGenModel()

        model.start_session("gemini-3-flash-preview")

        mock_chat.assert_called_once()
        assert model.client is not None

    @patch("src.application.models.google_gen.ChatGoogleGenerativeAI")
    def test_start_session_uses_correct_model_name(self, mock_chat):
        model = GoogleGenModel()

        model.start_session("gemini-2.5-pro")

        mock_chat.assert_called_with(model="gemini-2.5-pro")

    def test_start_session_raises_error_for_invalid_model(self):
        model = GoogleGenModel()

        with pytest.raises(ValueError, match="is not supported"):
            model.start_session("invalid-model")

    @patch("src.application.models.google_gen.ChatGoogleGenerativeAI")
    def test_get_model_after_session_started(self, mock_chat):
        model = GoogleGenModel()
        mock_chat.return_value = Mock()

        model.start_session("gemini-3-flash-preview")
        result = model.get_model()

        assert result == mock_chat.return_value
