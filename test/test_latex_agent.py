import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from uuid import uuid4

from src.application.agents.latex_agent import (
    latex_agent,
    re_do_latex,
    write_and_compile_latex,
    format_to_latex,
    format_to_latex_agent,
    get_all_tex,
    header_to_latex,
    education_to_latex,
    work_experience_to_latex,
    technical_skills_to_latex,
    certifications_to_latex,
    projects_to_latex,
)
from src.domain.orq_models import AppState


@pytest.fixture
def mock_app_state():
    state = Mock(spec=AppState)
    state.validation_agent_recommendations = {}
    state.experience_info = Mock()
    state.projects_info = Mock()
    state.header_info = Mock()
    state.skills_info = Mock()
    state.education_info = Mock()
    state.certifications_info = Mock()
    state.llm_model = Mock()
    return state


@pytest.mark.asyncio
@patch('src.application.agents.latex_agent.format_to_latex')
@patch('src.application.agents.latex_agent.get_all_tex')
@patch('src.application.agents.latex_agent.write_and_compile_latex')
async def test_latex_agent_returns_path_uri_with_compiled_file(mock_write, mock_get_tex, mock_format, mock_app_state):
    mock_format.return_value = mock_app_state
    mock_get_tex.return_value = "\\documentclass{article}"
    mock_write.return_value = "cv_output_20240101_abc123.zip"

    result = await latex_agent(mock_app_state)

    assert "http://localhost:8080/api/v1/download_file/cv_output_20240101_abc123.zip" == result["latex_content"]
    mock_format.assert_called_once()
    mock_get_tex.assert_called_once()
    mock_write.assert_called_once()


@patch('src.application.agents.latex_agent.write_and_compile_latex')
def test_re_do_latex_compiles_provided_content(mock_write):
    mock_write.return_value = "cv_output_20240101_def456.zip"
    latex_content = "\\documentclass{article}\\begin{document}test\\end{document}"

    result = re_do_latex(latex_content)

    assert "http://localhost:8080/api/v1/download_file/cv_output_20240101_def456.zip" == result["response"]
    mock_write.assert_called_once_with(latex_content)


@patch('src.application.agents.latex_agent.subprocess.run')
@patch('src.application.agents.latex_agent.os.rename')
def test_write_and_compile_latex_creates_tex_file_and_generates_zip(mock_rename, mock_subprocess):
    with tempfile.TemporaryDirectory() as tmpdir:
        latex_content = "\\documentclass{article}\\begin{document}test\\end{document}"

        result = write_and_compile_latex(latex_content, tmpdir)

        assert os.path.exists(os.path.join(tmpdir, "final_tex.tex"))
        assert mock_subprocess.call_count == 2
        assert mock_rename.called


@patch('src.application.agents.latex_agent.subprocess.run')
def test_write_and_compile_latex_calls_pdflatex_with_correct_arguments(mock_subprocess):
    with tempfile.TemporaryDirectory() as tmpdir:
        latex_content = "test content"

        write_and_compile_latex(latex_content, tmpdir)

        first_call = mock_subprocess.call_args_list[0]
        assert "pdflatex" in first_call[0][0]
        assert "-interaction=nonstopmode" in first_call[0][0]


@patch('src.application.agents.latex_agent.subprocess.run')
def test_write_and_compile_latex_calls_zip_with_correct_files(mock_subprocess):
    with tempfile.TemporaryDirectory() as tmpdir:
        latex_content = "test content"

        write_and_compile_latex(latex_content, tmpdir)

        second_call = mock_subprocess.call_args_list[1]
        assert "zip" in second_call[0][0]
        assert "final_tex.tex" in second_call[0][0]
        assert "final_tex.pdf" in second_call[0][0]


@patch('src.application.agents.latex_agent.subprocess.run')
@patch('src.application.agents.latex_agent.os.rename')
def test_write_and_compile_latex_generates_unique_filenames(mock_rename, mock_subprocess):
    with tempfile.TemporaryDirectory() as tmpdir:
        latex_content = "test"

        result1 = write_and_compile_latex(latex_content, tmpdir)
        result2 = write_and_compile_latex(latex_content, tmpdir)

        assert result1 != result2
        assert result1.startswith("cv_output_")
        assert result2.startswith("cv_output_")


@patch('src.application.agents.latex_agent.subprocess.run')
def test_write_and_compile_latex_raises_error_if_pdflatex_fails(mock_subprocess):
    mock_subprocess.side_effect = Exception("pdflatex failed")

    with pytest.raises(Exception):
        write_and_compile_latex("test", tempfile.gettempdir())


@pytest.mark.asyncio
@patch('src.application.agents.latex_agent.format_to_latex_agent')
async def test_format_to_latex_calls_agent_for_each_section(mock_agent, mock_app_state):
    mock_agent.return_value = Mock()

    await format_to_latex(mock_app_state)

    assert mock_agent.call_count == 6


@pytest.mark.asyncio
@patch('src.application.agents.latex_agent.format_to_latex_agent')
async def test_format_to_latex_updates_app_state_with_formatted_results(mock_agent, mock_app_state):
    formatted_experience = Mock()
    formatted_projects = Mock()
    formatted_header = Mock()
    formatted_skills = Mock()
    formatted_education = Mock()
    formatted_certifications = Mock()

    mock_agent.side_effect = [
        formatted_experience, formatted_projects, formatted_header,
        formatted_skills, formatted_education, formatted_certifications
    ]

    result = await format_to_latex(mock_app_state)

    assert result.experience_info == formatted_experience
    assert result.projects_info == formatted_projects
    assert result.header_info == formatted_header
    assert result.skills_info == formatted_skills
    assert result.education_info == formatted_education
    assert result.certifications_info == formatted_certifications


@pytest.mark.asyncio
@patch('src.application.agents.latex_agent.format_to_latex_agent')
async def test_format_to_latex_agent_sends_correct_prompt_to_llm(mock_agent, mock_app_state):
    mock_llm = Mock()
    mock_llm.with_structured_output.return_value.ainvoke = AsyncMock(return_value=Mock())
    mock_app_state.llm_model.get_model.return_value = mock_llm

    test_data = '{"test": "data"}'
    await format_to_latex_agent(mock_app_state, test_data, Mock)

    mock_llm.with_structured_output.assert_called_once()


@patch('builtins.open', create=True)
def test_get_all_tex_combines_all_sections(mock_open):
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = "\\documentclass{article}"
    mock_open.return_value = mock_file

    mock_app_state = Mock(spec=AppState)
    mock_app_state.header_info = Mock()
    mock_app_state.education_info = Mock()
    mock_app_state.experience_info = Mock()
    mock_app_state.skills_info = Mock()
    mock_app_state.certifications_info = Mock()
    mock_app_state.projects_info = Mock()

    with patch('src.application.agents.latex_agent.header_to_latex', return_value="\n% HEADER"):
        with patch('src.application.agents.latex_agent.education_to_latex', return_value="\n% EDUCATION"):
            with patch('src.application.agents.latex_agent.work_experience_to_latex', return_value="\n% EXPERIENCE"):
                with patch('src.application.agents.latex_agent.technical_skills_to_latex', return_value="\n% SKILLS"):
                    with patch('src.application.agents.latex_agent.certifications_to_latex', return_value="\n% CERTS"):
                        with patch('src.application.agents.latex_agent.projects_to_latex', return_value="\n% PROJECTS"):
                            result = get_all_tex(mock_app_state)

    assert "HEADER" in result
    assert "EDUCATION" in result
    assert "EXPERIENCE" in result
    assert "SKILLS" in result
    assert "CERTS" in result
    assert "PROJECTS" in result


def test_header_to_latex_formats_name_and_contact_info(mock_app_state):
    header = Mock()
    header.name = "John Doe"
    header.about_me = "Software Engineer"
    header.title = "Senior Developer"
    header.phone = "123-456-7890"
    header.mail = "john@example.com"
    header.github = "https://github.com/johndoe"
    header.linkedin = "https://linkedin.com/in/johndoe"
    header.city = "New York"
    header.country = "USA"
    mock_app_state.header_info = header

    result = header_to_latex(mock_app_state)

    assert "John Doe" in result
    assert "john@example.com" in result
    assert "123-456-7890" in result
    assert "New York, USA" in result


def test_education_to_latex_includes_degree_and_gpa(mock_app_state):
    education = Mock()
    education_entry = Mock()
    education_entry.degree = "Bachelor of Science"
    education_entry.institution = "MIT"
    education_entry.GPA = "3.9"
    education_entry.start_date = "2020"
    education_entry.end_date = "2024"
    education.education = [education_entry]
    education.relevant_courses = ["Algorithms", "Data Structures"]
    mock_app_state.education_info = education

    result = education_to_latex(mock_app_state)

    assert "Bachelor of Science" in result
    assert "MIT" in result
    assert "3.9" in result
    assert "Algorithms" in result


def test_education_to_latex_handles_multiple_entries(mock_app_state):
    education = Mock()
    entry1 = Mock(degree="BS", institution="MIT", GPA="3.9", start_date="2020", end_date="2024")
    entry2 = Mock(degree="MS", institution="Stanford", GPA="4.0", start_date="2024", end_date="2026")
    education.education = [entry1, entry2]
    education.relevant_courses = []
    mock_app_state.education_info = education

    result = education_to_latex(mock_app_state)

    assert "MIT" in result
    assert "Stanford" in result


def test_work_experience_to_latex_includes_company_and_responsibilities(mock_app_state):
    experience = Mock()
    job = Mock()
    job.company = "TechCorp"
    job.job_title = "Senior Engineer"
    job.start_date = "2022"
    job.end_date = "2024"
    job.responsibilities = ["Led team", "Designed system"]
    experience.work_experience = [job]
    mock_app_state.experience_info = experience

    result = work_experience_to_latex(mock_app_state)

    assert "TechCorp" in result
    assert "Senior Engineer" in result
    assert "Led team" in result
    assert "Designed system" in result


def test_technical_skills_to_latex_joins_skills_and_languages(mock_app_state):
    skills = Mock()
    skills.skills = ["Python", "Java", "C++"]
    skills.languages = ["English", "Spanish"]
    mock_app_state.skills_info = skills

    result = technical_skills_to_latex(mock_app_state)

    assert "Python" in result
    assert "Java" in result
    assert "English" in result


def test_certifications_to_latex_lists_all_certifications(mock_app_state):
    certs = Mock()
    certs.certifications = ["AWS Certified", "GCP Certified", "Azure Certified"]
    mock_app_state.certifications_info = certs

    result = certifications_to_latex(mock_app_state)

    assert "AWS Certified" in result
    assert "GCP Certified" in result
    assert "Azure Certified" in result


def test_projects_to_latex_includes_project_names_and_technologies(mock_app_state):
    projects = Mock()
    project = Mock()
    project.project_name = "AI Engine"
    project.description = "Built ML pipeline\nOptimized performance"
    project.technologies_used = ["Python", "TensorFlow"]
    projects.projects = [project]
    mock_app_state.projects_info = projects

    result = projects_to_latex(mock_app_state)

    assert "AI Engine" in result
    assert "Built ML pipeline" in result
    assert "Python" in result
    assert "TensorFlow" in result


def test_projects_to_latex_handles_empty_technologies_list(mock_app_state):
    projects = Mock()
    project = Mock()
    project.project_name = "Simple Project"
    project.description = "Did something"
    project.technologies_used = []
    projects.projects = [project]
    mock_app_state.projects_info = projects

    result = projects_to_latex(mock_app_state)

    assert "Simple Project" in result
    assert "Did something" in result


def test_projects_to_latex_includes_closing_text_when_provided(mock_app_state):
    projects = Mock()
    projects.projects = []
    mock_app_state.projects_info = projects

    result = projects_to_latex(mock_app_state, "Contact me for details")

    assert "Contact me for details" in result


def test_projects_to_latex_handles_multiline_descriptions(mock_app_state):
    projects = Mock()
    project = Mock()
    project.project_name = "Project"
    project.description = "Line 1\nLine 2\nLine 3"
    project.technologies_used = []
    projects.projects = [project]
    mock_app_state.projects_info = projects

    result = projects_to_latex(mock_app_state)

    assert "Line 1" in result
    assert "Line 2" in result
    assert "Line 3" in result