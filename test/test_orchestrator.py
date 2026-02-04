"""
Tests para el orquestador de agentes (graph_orq.py)
"""
import pytest
from unittest.mock import Mock, patch

from src.application.orquestrator.graph_orq import (
    parallel_research_node,
    orchestrator,
)
from src.domain.orq_models import AppState


@pytest.fixture
def mock_app_state():
    state = Mock(spec=AppState)
    state.llm_model = Mock()
    state.language_to_respond = "en"
    state.personal_json = {}
    state.postulation_info = "Developer position"
    state.model_copy = Mock(return_value=state)
    return state


class TestParallelResearchNode:
    @pytest.mark.asyncio
    @patch("src.application.orquestrator.graph_orq.header_agent")
    @patch("src.application.orquestrator.graph_orq.education_agent")
    @patch("src.application.orquestrator.graph_orq.work_agent")
    @patch("src.application.orquestrator.graph_orq.tech_agent")
    @patch("src.application.orquestrator.graph_orq.cert_agent")
    @patch("src.application.orquestrator.graph_orq.projects_agent")
    async def test_calls_all_agents_in_parallel(
        self, mock_projects, mock_cert, mock_tech, mock_work, mock_edu, mock_header, mock_app_state
    ):
        mock_header.return_value = {"header_info": Mock()}
        mock_edu.return_value = {"education_info": Mock()}
        mock_work.return_value = {"experience_info": Mock()}
        mock_tech.return_value = {"skills_info": Mock()}
        mock_cert.return_value = {"certifications_info": Mock()}
        mock_projects.return_value = {"projects_info": Mock()}

        await parallel_research_node(mock_app_state)

        mock_header.assert_called_once_with(mock_app_state)
        mock_edu.assert_called_once_with(mock_app_state)
        mock_work.assert_called_once_with(mock_app_state)
        mock_tech.assert_called_once_with(mock_app_state)
        mock_cert.assert_called_once_with(mock_app_state)
        mock_projects.assert_called_once_with(mock_app_state)

    @pytest.mark.asyncio
    @patch("src.application.orquestrator.graph_orq.header_agent")
    @patch("src.application.orquestrator.graph_orq.education_agent")
    @patch("src.application.orquestrator.graph_orq.work_agent")
    @patch("src.application.orquestrator.graph_orq.tech_agent")
    @patch("src.application.orquestrator.graph_orq.cert_agent")
    @patch("src.application.orquestrator.graph_orq.projects_agent")
    async def test_combines_all_agent_results(
        self, mock_projects, mock_cert, mock_tech, mock_work, mock_edu, mock_header, mock_app_state
    ):
        header_result = {"header_info": "header"}
        edu_result = {"education_info": "edu"}
        work_result = {"experience_info": "work"}
        tech_result = {"skills_info": "tech"}
        cert_result = {"certifications_info": "cert"}
        projects_result = {"projects_info": "projects"}

        mock_header.return_value = header_result
        mock_edu.return_value = edu_result
        mock_work.return_value = work_result
        mock_tech.return_value = tech_result
        mock_cert.return_value = cert_result
        mock_projects.return_value = projects_result

        result = await parallel_research_node(mock_app_state)

        assert result["header_info"] == "header"
        assert result["education_info"] == "edu"
        assert result["experience_info"] == "work"
        assert result["skills_info"] == "tech"
        assert result["certifications_info"] == "cert"
        assert result["projects_info"] == "projects"

    @pytest.mark.asyncio
    @patch("src.application.orquestrator.graph_orq.header_agent")
    @patch("src.application.orquestrator.graph_orq.education_agent")
    @patch("src.application.orquestrator.graph_orq.work_agent")
    @patch("src.application.orquestrator.graph_orq.tech_agent")
    @patch("src.application.orquestrator.graph_orq.cert_agent")
    @patch("src.application.orquestrator.graph_orq.projects_agent")
    async def test_handles_none_results_gracefully(
        self, mock_projects, mock_cert, mock_tech, mock_work, mock_edu, mock_header, mock_app_state
    ):
        mock_header.return_value = {"header_info": "header"}
        mock_edu.return_value = None
        mock_work.return_value = {"experience_info": "work"}
        mock_tech.return_value = None
        mock_cert.return_value = {"certifications_info": "cert"}
        mock_projects.return_value = None

        result = await parallel_research_node(mock_app_state)

        assert result["header_info"] == "header"
        assert result["experience_info"] == "work"
        assert result["certifications_info"] == "cert"
        assert "education_info" not in result


class TestOrchestrator:
    @pytest.mark.asyncio
    @patch("src.application.orquestrator.graph_orq.parallel_research_node")
    @patch("src.application.orquestrator.graph_orq.latex_agent")
    async def test_returns_response_with_latex_content(
        self, mock_latex, mock_parallel, mock_app_state
    ):
        mock_parallel.return_value = {"header_info": Mock()}
        mock_latex.return_value = {"latex_content": "http://example.com/cv.zip"}

        result = await orchestrator(mock_app_state)

        assert result == {"response": "http://example.com/cv.zip"}

    @pytest.mark.asyncio
    @patch("src.application.orquestrator.graph_orq.parallel_research_node")
    @patch("src.application.orquestrator.graph_orq.latex_agent")
    async def test_calls_parallel_research_first(
        self, mock_latex, mock_parallel, mock_app_state
    ):
        mock_parallel.return_value = {}
        mock_latex.return_value = {"latex_content": "result"}

        await orchestrator(mock_app_state)

        mock_parallel.assert_called_once_with(mock_app_state)

    @pytest.mark.asyncio
    @patch("src.application.orquestrator.graph_orq.parallel_research_node")
    @patch("src.application.orquestrator.graph_orq.latex_agent")
    async def test_updates_state_with_collected_data(
        self, mock_latex, mock_parallel, mock_app_state
    ):
        collected_data = {"header_info": "test", "education_info": "test2"}
        mock_parallel.return_value = collected_data
        mock_latex.return_value = {"latex_content": "result"}

        await orchestrator(mock_app_state)

        mock_app_state.model_copy.assert_called_once_with(update=collected_data)

    @pytest.mark.asyncio
    @patch("src.application.orquestrator.graph_orq.parallel_research_node")
    @patch("src.application.orquestrator.graph_orq.latex_agent")
    async def test_calls_latex_agent_after_research(
        self, mock_latex, mock_parallel, mock_app_state
    ):
        mock_parallel.return_value = {}
        updated_state = Mock()
        mock_app_state.model_copy.return_value = updated_state
        mock_latex.return_value = {"latex_content": "result"}

        await orchestrator(mock_app_state)

        mock_latex.assert_called_once_with(updated_state)
