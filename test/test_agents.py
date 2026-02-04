"""
Tests para los agentes de procesamiento de CV
"""
import pytest
from unittest.mock import Mock, AsyncMock

from src.application.agents.header_agent import header_agent
from src.application.agents.education_agent import education_agent
from src.application.agents.work_exp_agent import work_agent
from src.application.agents.technical_agent import tech_agent
from src.application.agents.certification_agent import cert_agent
from src.application.agents.projects_agent import projects_agent
from src.domain.orq_models import AppState


@pytest.fixture
def mock_app_state():
    state = Mock(spec=AppState)
    state.language_to_respond = "en"
    state.postulation_info = "Software Engineer position"
    state.llm_model = Mock()
    mock_llm = Mock()
    mock_llm.with_structured_output.return_value.ainvoke = AsyncMock()
    state.llm_model.get_model.return_value = mock_llm
    return state


class TestHeaderAgent:
    @pytest.mark.asyncio
    async def test_returns_header_info_key(self, mock_app_state):
        mock_app_state.personal_json = {"header": {"name": "John Doe"}}
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = AsyncMock(
            return_value=Mock()
        )

        result = await header_agent(mock_app_state)

        assert "header_info" in result

    @pytest.mark.asyncio
    async def test_raises_error_when_header_missing(self, mock_app_state):
        mock_app_state.personal_json = {}

        with pytest.raises(ValueError, match="Must provide Header data"):
            await header_agent(mock_app_state)

    @pytest.mark.asyncio
    async def test_uses_correct_language(self, mock_app_state):
        mock_app_state.personal_json = {"header": {"name": "John"}}
        mock_app_state.language_to_respond = "Spanish"
        mock_invoke = AsyncMock(return_value=Mock())
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = mock_invoke

        await header_agent(mock_app_state)

        call_args = mock_invoke.call_args[0][0]
        assert any("Spanish" in str(msg) for msg in call_args)


class TestEducationAgent:
    @pytest.mark.asyncio
    async def test_returns_education_info_key(self, mock_app_state):
        mock_app_state.personal_json = {
            "education": [{"degree": "BS"}],
            "relevant_courses": ["Algorithms"]
        }
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = AsyncMock(
            return_value=Mock()
        )

        result = await education_agent(mock_app_state)

        assert "education_info" in result

    @pytest.mark.asyncio
    async def test_raises_error_when_education_missing(self, mock_app_state):
        mock_app_state.personal_json = {}

        with pytest.raises(ValueError, match="Must provide educational data"):
            await education_agent(mock_app_state)

    @pytest.mark.asyncio
    async def test_raises_error_when_courses_missing(self, mock_app_state):
        mock_app_state.personal_json = {"education": [{"degree": "BS"}]}

        with pytest.raises(ValueError, match="Must provide educational data"):
            await education_agent(mock_app_state)

    @pytest.mark.asyncio
    async def test_combines_education_and_courses_in_prompt(self, mock_app_state):
        mock_app_state.personal_json = {
            "education": [{"degree": "BS", "institution": "MIT"}],
            "relevant_courses": ["Algorithms", "Data Structures"]
        }
        mock_invoke = AsyncMock(return_value=Mock())
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = mock_invoke

        await education_agent(mock_app_state)

        call_args = mock_invoke.call_args[0][0]
        prompt_content = str(call_args)
        assert "MIT" in prompt_content or "Algorithms" in prompt_content


class TestWorkAgent:
    @pytest.mark.asyncio
    async def test_returns_experience_info_key(self, mock_app_state):
        mock_app_state.personal_json = {"work_experience": [{"company": "TechCorp"}]}
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = AsyncMock(
            return_value=Mock()
        )

        result = await work_agent(mock_app_state)

        assert "experience_info" in result

    @pytest.mark.asyncio
    async def test_raises_error_when_work_missing(self, mock_app_state):
        mock_app_state.personal_json = {}

        with pytest.raises(ValueError, match="Must provide work data"):
            await work_agent(mock_app_state)

    @pytest.mark.asyncio
    async def test_includes_postulation_info_in_prompt(self, mock_app_state):
        mock_app_state.personal_json = {"work_experience": [{"company": "Corp"}]}
        mock_app_state.postulation_info = "Senior Developer role"
        mock_invoke = AsyncMock(return_value=Mock())
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = mock_invoke

        await work_agent(mock_app_state)

        call_args = mock_invoke.call_args[0][0]
        prompt_content = str(call_args)
        assert "Senior Developer role" in prompt_content


class TestTechAgent:
    @pytest.mark.asyncio
    async def test_returns_skills_info_key(self, mock_app_state):
        mock_app_state.personal_json = {"technical_skills": ["Python", "Java"]}
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = AsyncMock(
            return_value=Mock()
        )

        result = await tech_agent(mock_app_state)

        assert "skills_info" in result

    @pytest.mark.asyncio
    async def test_raises_error_when_tech_missing(self, mock_app_state):
        mock_app_state.personal_json = {}

        with pytest.raises(ValueError, match="Must provide tech data"):
            await tech_agent(mock_app_state)


class TestCertAgent:
    @pytest.mark.asyncio
    async def test_returns_certifications_info_key(self, mock_app_state):
        mock_app_state.personal_json = {"certifications": ["AWS Certified"]}
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = AsyncMock(
            return_value=Mock()
        )

        result = await cert_agent(mock_app_state)

        assert "certifications_info" in result

    @pytest.mark.asyncio
    async def test_raises_error_when_certifications_missing(self, mock_app_state):
        mock_app_state.personal_json = {}

        with pytest.raises(ValueError, match="Must provide certification data"):
            await cert_agent(mock_app_state)


class TestProjectsAgent:
    @pytest.mark.asyncio
    async def test_returns_projects_info_key(self, mock_app_state):
        mock_app_state.personal_json = {"projects": [{"name": "AI Project"}]}
        mock_app_state.llm_model.get_model.return_value.with_structured_output.return_value.ainvoke = AsyncMock(
            return_value=Mock()
        )

        result = await projects_agent(mock_app_state)

        assert "projects_info" in result

    @pytest.mark.asyncio
    async def test_raises_error_when_projects_missing(self, mock_app_state):
        mock_app_state.personal_json = {}

        with pytest.raises(ValueError, match="Must provide projects data"):
            await projects_agent(mock_app_state)
