"""
Tests para el módulo de API (infrastructure/api.py)
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
import os

from src.infrastructure.api import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestProcessEndpoint:
    @pytest.mark.asyncio
    @patch("src.infrastructure.api.models_registry")
    @patch("src.infrastructure.api.orchestrator")
    async def test_valid_request_returns_result(self, mock_orchestrator, mock_registry):
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
    def test_invalid_json_template_returns_400(self, mock_registry):
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
    async def test_orchestrator_exception_returns_400(self, mock_orchestrator, mock_registry):
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

    @patch("src.infrastructure.api.models_registry")
    def test_empty_json_template_returns_400(self, mock_registry):
        mock_llm = MagicMock()
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm

        request_data = {
            "llm_vendor": "openai",
            "model": "gpt-4",
            "json_template": "",
            "response_language": "en",
            "job_offer": "Software Engineer"
        }

        response = client.post("/process", json=request_data)
        assert response.status_code == 400

    def test_missing_required_fields_returns_422(self):
        request_data = {
            "llm_vendor": "openai",
            "model": "gpt-4"
        }

        response = client.post("/process", json=request_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("src.infrastructure.api.models_registry")
    @patch("src.infrastructure.api.orchestrator")
    async def test_starts_llm_session_with_correct_model(self, mock_orchestrator, mock_registry):
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

        client.post("/process", json=request_data)
        mock_llm.start_session.assert_called_once_with("gpt-4")

    @patch("src.infrastructure.api.models_registry")
    @patch("src.infrastructure.api.orchestrator")
    def test_nested_json_template_accepted(self, mock_orchestrator, mock_registry):
        mock_llm = MagicMock()
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm
        mock_orchestrator.return_value = {"status": "success"}

        request_data = {
            "llm_vendor": "openai",
            "model": "gpt-4",
            "json_template": '{"person": {"name": "John", "skills": ["python", "java"]}}',
            "response_language": "es",
            "job_offer": "Software Engineer"
        }

        response = client.post("/process", json=request_data)
        assert response.status_code == 200


class TestReProcessTexEndpoint:
    @patch("src.infrastructure.api.re_do_latex")
    def test_valid_request_returns_result(self, mock_re_do_latex):
        mock_re_do_latex.return_value = {"status": "processed"}

        request_data = {"new_tex": "\\documentclass{article}"}

        response = client.post("/re_process_tex", json=request_data)
        assert response.status_code == 200
        mock_re_do_latex.assert_called_once_with("\\documentclass{article}")

    @patch("src.infrastructure.api.re_do_latex")
    def test_empty_tex_processed(self, mock_re_do_latex):
        mock_re_do_latex.return_value = {"status": "processed"}

        request_data = {"new_tex": ""}

        response = client.post("/re_process_tex", json=request_data)
        assert response.status_code == 200
        mock_re_do_latex.assert_called_once_with("")

    @patch("src.infrastructure.api.re_do_latex")
    def test_complex_latex_document(self, mock_re_do_latex):
        mock_re_do_latex.return_value = {"status": "processed"}

        complex_tex = """\\documentclass{article}
\\begin{document}
\\section{Introduction}
Hello World
\\end{document}"""

        request_data = {"new_tex": complex_tex}

        response = client.post("/re_process_tex", json=request_data)
        assert response.status_code == 200
        mock_re_do_latex.assert_called_once_with(complex_tex)

    def test_missing_new_tex_field_returns_422(self):
        request_data = {}

        response = client.post("/re_process_tex", json=request_data)
        assert response.status_code == 422


class TestGetAvailableVendorsEndpoint:
    @patch("src.infrastructure.api.models_registry")
    def test_returns_list_of_vendors(self, mock_registry):
        mock_registry.keys.return_value = ["openai", "anthropic"]

        response = client.get("/available_vendors")
        assert response.status_code == 200
        assert response.json() == {"available_vendors": ["openai", "anthropic"]}

    @patch("src.infrastructure.api.models_registry")
    def test_empty_registry_returns_empty_list(self, mock_registry):
        mock_registry.keys.return_value = []

        response = client.get("/available_vendors")
        assert response.status_code == 200
        assert response.json() == {"available_vendors": []}

    @patch("src.infrastructure.api.models_registry")
    def test_single_vendor_returns_single_item(self, mock_registry):
        mock_registry.keys.return_value = ["google"]

        response = client.get("/available_vendors")
        assert response.status_code == 200
        assert response.json() == {"available_vendors": ["google"]}


class TestGetAvailableModelsEndpoint:
    @patch("src.infrastructure.api.models_registry")
    def test_valid_vendor_returns_models(self, mock_registry):
        mock_llm = MagicMock()
        mock_llm.get_available_models.return_value = ["gpt-4", "gpt-3.5-turbo"]
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm

        response = client.get("/available_models/openai")
        assert response.status_code == 200
        assert response.json() == {"available_models": ["gpt-4", "gpt-3.5-turbo"]}

    @patch("src.infrastructure.api.models_registry")
    def test_invalid_vendor_returns_400(self, mock_registry):
        mock_registry.keys.return_value = ["openai"]

        response = client.get("/available_models/invalid_vendor")
        assert response.status_code == 400

    @patch("src.infrastructure.api.models_registry")
    def test_empty_models_list_returns_empty(self, mock_registry):
        mock_llm = MagicMock()
        mock_llm.get_available_models.return_value = []
        mock_registry.keys.return_value = ["openai"]
        mock_registry.get.return_value = mock_llm

        response = client.get("/available_models/openai")
        assert response.status_code == 200
        assert response.json() == {"available_models": []}

    @patch("src.infrastructure.api.models_registry")
    def test_case_sensitive_vendor_name(self, mock_registry):
        mock_registry.keys.return_value = ["openai"]

        response = client.get("/available_models/OpenAI")
        assert response.status_code == 400


class TestDownloadFileEndpoint:
    @patch("os.path.exists")
    def test_valid_zip_with_file_existing(self, mock_exists):
        mock_exists.return_value = True

        with patch("src.infrastructure.api.FileResponse") as mock_file_response:
            mock_file_response.return_value = MagicMock()
            response = client.get("/download_file/test.zip")

    def test_non_zip_returns_400(self):
        response = client.get("/download_file/test.pdf")
        assert response.status_code == 400
        assert "Only .zip files can be downloaded" in response.json()["detail"]

    @patch("os.path.exists")
    def test_not_found_returns_404(self, mock_exists):
        mock_exists.return_value = False

        response = client.get("/download_file/nonexistent.zip")
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    @patch("os.path.exists")
    def test_constructs_correct_path(self, mock_exists):
        mock_exists.return_value = False

        client.get("/download_file/myfile.zip")
        expected_path = os.path.join("/app", "src", "outputs", "myfile.zip")
        mock_exists.assert_called_with(expected_path)

    def test_txt_extension_returns_400(self):
        response = client.get("/download_file/test.txt")
        assert response.status_code == 400

    def test_empty_filename_with_zip_extension(self):
        response = client.get("/download_file/.zip")
        assert response.status_code in [400, 404]
