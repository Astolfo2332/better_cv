import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json
import os

from src.infrastructure.api import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def test_mock_models_registry():
    mock_llm = MagicMock()
    mock_llm.get_available_models.return_value = ["model1", "model2"]
    mock_llm.start_session = MagicMock()
    return {"openai": mock_llm, "anthropic": mock_llm}

class TestProcessEndpoint:
    @pytest.mark.asyncio
    @patch("src.infrastructure.api.models_registry")
    @patch("src.infrastructure.api.orchestrator")
    async def test_process_valid_request_returns_result(self, mock_orchestrator, mock_registry):
        mock_llm = MagicMock()
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm
        mock_orchestrator.return_value = {"status": "success"}

        request_data = {
            "llm_vendor": "openai",
            "model": "gpt-4",
            "json_template": '{"name": "John"}',
            "response_language": "en",
            "job_offer": "Software Engineer"
        }

        response = client.post("/process", json=request_data)
        assert response.status_code == 200

    @patch("src.infrastructure.api.models_registry")
    def test_process_invalid_json_template_returns_400(self, mock_registry):
        mock_llm = MagicMock()
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm

        request_data = {
            "llm_vendor": "openai",
            "model": "gpt-4",
            "json_template": "invalid json {",
            "response_language": "en",
            "job_offer": "Software Engineer"
        }

        response = client.post("/process", json=request_data)
        assert response.status_code == 400
        assert "Invalid JSON template" in response.json()["detail"]

    @pytest.mark.asyncio
    @patch("src.infrastructure.api.models_registry")
    @patch("src.infrastructure.api.orchestrator")
    async def test_process_orchestrator_exception_returns_400(self, mock_orchestrator, mock_registry):
        mock_llm = MagicMock()
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm
        mock_orchestrator.side_effect = Exception("Orchestrator error")

        request_data = {
            "llm_vendor": "openai",
            "model": "gpt-4",
            "json_template": '{"name": "John"}',
            "response_language": "en",
            "job_offer": "Software Engineer"
        }

        response = client.post("/process", json=request_data)
        assert response.status_code == 400


class TestReProcessTexEndpoint:
    @patch("src.infrastructure.api.re_do_latex")
    def test_re_process_tex_valid_request_returns_result(self, mock_re_do_latex):
        mock_re_do_latex.return_value = {"status": "processed"}

        request_data = {"new_tex": "\\documentclass{article}"}

        response = client.post("/re_process_tex", json=request_data)
        assert response.status_code == 200
        mock_re_do_latex.assert_called_once_with("\\documentclass{article}")


class TestGetAvailableVendorsEndpoint:
    @patch("src.infrastructure.api.models_registry")
    def test_available_vendors_returns_list_of_vendors(self, mock_registry):
        mock_registry.keys.return_value = ["openai", "anthropic"]

        response = client.get("/available_vendors")
        assert response.status_code == 200
        assert response.json() == {"available_vendors": ["openai", "anthropic"]}


class TestGetAvailableModelsEndpoint:
    @patch("src.infrastructure.api.models_registry")
    def test_available_models_valid_vendor_returns_models(self, mock_registry):
        mock_llm = MagicMock()
        mock_llm.get_available_models.return_value = ["gpt-4", "gpt-3.5-turbo"]
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm

        response = client.get("/available_models/openai")
        assert response.status_code == 200
        assert response.json() == {"available_models": ["gpt-4", "gpt-3.5-turbo"]}

    @patch("src.infrastructure.api.models_registry")
    def test_available_models_invalid_vendor_returns_400(self, mock_registry):
        mock_registry.keys.return_value = ["openai"]

        response = client.get("/available_models/invalid_vendor")
        assert response.status_code == 400


class TestDownloadFileEndpoint:
    @patch("os.path.exists")
    def test_download_file_valid_zip_returns_file(self, mock_exists):
        mock_exists.return_value = True

        with patch("src.infrastructure.api.FileResponse") as mock_file_response:
            mock_file_response.return_value = MagicMock()
            response = client.get("/download_file/test.zip")

    def test_download_file_non_zip_returns_400(self):
        response = client.get("/download_file/test.pdf")
        assert response.status_code == 400
        assert "Only .zip files can be downloaded" in response.json()["detail"]

    @patch("os.path.exists")
    def test_download_file_not_found_returns_404(self, mock_exists):
        mock_exists.return_value = False

        response = client.get("/download_file/nonexistent.zip")
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    @patch("os.path.exists")
    def test_download_file_constructs_correct_path(self, mock_exists):
        mock_exists.return_value = False

        client.get("/download_file/myfile.zip")
        expected_path = os.path.join("/app", "src", "outputs", "myfile.zip")
        mock_exists.assert_called_with(expected_path)