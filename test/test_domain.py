"""
Tests para los modelos de dominio (cv_models, orq_models, request_models)
"""
import pytest
from pydantic import ValidationError

from src.domain.cv_models import (
    Header,
    EducationEntry,
    EducationField,
    WorkExperienceEntry,
    WorkExperienceField,
    SkillSetField,
    CertificationsField,
    ProjectEntry,
    ProjectsField,
)
from src.domain.orq_models import AppState
from src.domain.request_models import Request, ReProcessTexRequest


class TestHeader:
    def test_creates_valid_header(self):
        header = Header(
            title="Software Engineer",
            name="John Doe",
            mail="john@example.com",
            phone="123-456-7890",
            linkedin="https://linkedin.com/in/johndoe",
            github="https://github.com/johndoe",
            country="USA",
            city="New York",
            about_me="Experienced developer"
        )

        assert header.name == "John Doe"
        assert header.mail == "john@example.com"

    def test_requires_all_fields(self):
        with pytest.raises(ValidationError):
            Header(name="John Doe")


class TestEducationEntry:
    def test_creates_valid_entry(self):
        entry = EducationEntry(
            degree="Bachelor of Science",
            institution="MIT",
            start_date="2020",
            end_date="2024",
            GPA="3.9"
        )

        assert entry.degree == "Bachelor of Science"
        assert entry.institution == "MIT"

    def test_requires_all_fields(self):
        with pytest.raises(ValidationError):
            EducationEntry(degree="BS")


class TestEducationField:
    def test_creates_with_empty_lists(self):
        field = EducationField(education=[], relevant_courses=[])

        assert field.education == []
        assert field.relevant_courses == []

    def test_creates_with_entries(self):
        entry = EducationEntry(
            degree="BS", institution="MIT", start_date="2020",
            end_date="2024", GPA="3.9"
        )
        field = EducationField(education=[entry], relevant_courses=["Algorithms"])

        assert len(field.education) == 1
        assert "Algorithms" in field.relevant_courses


class TestWorkExperienceEntry:
    def test_creates_valid_entry(self):
        entry = WorkExperienceEntry(
            job_title="Senior Engineer",
            company="TechCorp",
            start_date="2022",
            end_date="2024",
            responsibilities=["Led team", "Designed systems"]
        )

        assert entry.job_title == "Senior Engineer"
        assert len(entry.responsibilities) == 2

    def test_allows_empty_responsibilities(self):
        entry = WorkExperienceEntry(
            job_title="Engineer",
            company="Corp",
            start_date="2022",
            end_date="2024",
            responsibilities=[]
        )

        assert entry.responsibilities == []


class TestWorkExperienceField:
    def test_creates_with_entries(self):
        entry = WorkExperienceEntry(
            job_title="Engineer", company="Corp",
            start_date="2022", end_date="2024", responsibilities=[]
        )
        field = WorkExperienceField(work_experience=[entry])

        assert len(field.work_experience) == 1


class TestSkillSetField:
    def test_creates_with_skills_and_languages(self):
        field = SkillSetField(
            skills=["Python", "Java", "C++"],
            languages=["English", "Spanish"]
        )

        assert "Python" in field.skills
        assert "English" in field.languages

    def test_allows_empty_lists(self):
        field = SkillSetField(skills=[], languages=[])

        assert field.skills == []
        assert field.languages == []


class TestCertificationsField:
    def test_creates_with_certifications(self):
        field = CertificationsField(
            certifications=["AWS Certified", "GCP Certified"]
        )

        assert len(field.certifications) == 2

    def test_allows_empty_list(self):
        field = CertificationsField(certifications=[])

        assert field.certifications == []


class TestProjectEntry:
    def test_creates_valid_entry(self):
        entry = ProjectEntry(
            project_name="AI Engine",
            description="Built ML pipeline",
            technologies_used=["Python", "TensorFlow"]
        )

        assert entry.project_name == "AI Engine"
        assert "Python" in entry.technologies_used

    def test_allows_empty_technologies(self):
        entry = ProjectEntry(
            project_name="Simple Project",
            description="Did something",
            technologies_used=[]
        )

        assert entry.technologies_used == []


class TestProjectsField:
    def test_creates_with_projects(self):
        entry = ProjectEntry(
            project_name="Project", description="Desc", technologies_used=[]
        )
        field = ProjectsField(projects=[entry])

        assert len(field.projects) == 1


class TestAppState:
    def test_creates_with_defaults(self):
        state = AppState()

        assert state.llm_model is None
        assert state.header_info is None
        assert state.pass_validation is False
        assert state.personal_json == {}

    def test_creates_with_custom_values(self):
        state = AppState(
            language_to_respond="Spanish",
            postulation_info="Developer role",
            pass_validation=True
        )

        assert state.language_to_respond == "Spanish"
        assert state.postulation_info == "Developer role"
        assert state.pass_validation is True

    def test_model_copy_creates_new_instance(self):
        state = AppState(language_to_respond="English")
        new_state = state.model_copy(update={"language_to_respond": "Spanish"})

        assert state.language_to_respond == "English"
        assert new_state.language_to_respond == "Spanish"


class TestRequest:
    def test_creates_valid_request(self):
        request = Request(
            job_offer="Software Engineer",
            json_template='{"name": "John"}',
            llm_vendor="OpenAi",
            model="gpt-5.2",
            response_language="en"
        )

        assert request.job_offer == "Software Engineer"
        assert request.llm_vendor == "OpenAi"

    def test_requires_all_fields(self):
        with pytest.raises(ValidationError):
            Request(job_offer="Engineer")


class TestReProcessTexRequest:
    def test_creates_valid_request(self):
        request = ReProcessTexRequest(new_tex="\\documentclass{article}")

        assert request.new_tex == "\\documentclass{article}"

    def test_allows_empty_tex(self):
        request = ReProcessTexRequest(new_tex="")

        assert request.new_tex == ""

    def test_requires_new_tex_field(self):
        with pytest.raises(ValidationError):
            ReProcessTexRequest()
