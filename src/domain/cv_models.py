from pydantic import BaseModel, Field


class Header(BaseModel):
    title: str = Field(..., description="The title of the CV")
    name: str = Field(..., description="The full name of the individual")
    mail: str = Field(..., description="The email address of the individual")
    phone: str = Field(..., description="The phone number of the individual")
    linkedin: str = Field(..., description="The LinkedIn profile URL of the individual")
    github: str = Field(..., description="The GitHub profile URL of the individual")
    country: str = Field(..., description="The country of residence of the individual")
    city: str = Field(..., description="The city of residence of the individual")
    about_me: str = Field(..., description="A brief summary about the individual for the position")


class EducationEntry(BaseModel):
    degree: str = Field(..., description="The degree obtained")
    institution: str = Field(..., description="The name of the educational institution")
    start_date: str = Field(..., description="The start date of the education period")
    end_date: str = Field(..., description="The end date of the education period")
    GPA: str = Field(..., description="The GPA achieved")


class EducationField(BaseModel):
    education: list[EducationEntry] = Field(..., description="List of educational qualifications")
    relevant_courses: list[str] = Field(..., description="List of relevant courses taken")


class WorkExperienceEntry(BaseModel):
    job_title: str = Field(..., description="The job title held")
    company: str = Field(..., description="The name of the company")
    start_date: str = Field(..., description="The start date of the employment period")
    end_date: str = Field(..., description="The end date of the employment period")
    responsibilities: list[str] = Field(..., description="List of job responsibilities and achievements")


class WorkExperienceField(BaseModel):
    work_experience: list[WorkExperienceEntry] = Field(..., description="List of work experience entries")


class SkillSetField(BaseModel):
    skills: list[str] = Field(..., description="List of skills possessed by the individual")
    languages: list[str] = Field(..., description="List of languages known by the individual")


class CertificationsField(BaseModel):
    certifications: list[str] = Field(..., description="List of certifications obtained by the individual")


class ProjectEntry(BaseModel):
    project_name: str = Field(..., description="The name of the project")
    description: str = Field(..., description="A brief description of the project")
    technologies_used: list[str] = Field(..., description="List of technologies used in the project")


class ProjectsField(BaseModel):
    projects: list[ProjectEntry] = Field(..., description="List of projects undertaken by the individual")