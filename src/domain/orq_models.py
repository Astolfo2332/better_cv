from src.domain.cv_models import *
from typing import Any

class AppState(BaseModel):
    llm_model:Any = None
    header_info: Header = None
    education_info: EducationField = None
    experience_info: WorkExperienceField = None
    skills_info: SkillSetField = None
    certifications_info: CertificationsField = None
    projects_info: ProjectsField = None
    pass_validation: bool = False
    personal_json: dict = {}
    postulation_info: str = ""
    language_to_respond: str = ""
    validation_agent_recommendations:str = ""
    latex_content: str = ""