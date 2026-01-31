import asyncio
import os.path

from pydantic import BaseModel

from src.domain.orq_models import AppState
import subprocess
from src.application.agents.prompts.latex_prompts import latex_user_prompt, latex_system_message
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
from uuid import uuid4

PATH_FROM_URI = "http://localhost:8080/api/v1/download_file/"


async def latex_agent(app_state:AppState) -> dict:

    data_obj = {
        "ver_rec": app_state.validation_agent_recommendations,
    }

    app_state = await format_to_latex(app_state)

    final_text = get_all_tex(app_state)
    out_dir = "/app/src/outputs"
    with open(f"{out_dir}/final_tex.tex", "w", encoding="utf-8") as f:
        f.write(final_text)

    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", os.path.join(out_dir, "final_tex.tex")],
        cwd=out_dir,
        check=True,
    )
    #Se comprime el .tex y el .pdf en un zip
    subprocess.run(
        ["zip", "cv_output.zip", "final_tex.tex", "final_tex.pdf"],
        cwd=out_dir,
        check=True,
    )
    # Se cambia el nombre por una combinación de la fecha y un identificador único
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = uuid4().hex[:6]  # Obtener los primeros 6 caracteres de un UUID4
    file_rename = f"cv_output_{date_str}_{unique_id}.zip"
    os.rename(
        os.path.join(out_dir, "cv_output.zip"),
        os.path.join(out_dir, file_rename)
    )

    #TODO: Hacerlo más resiliente
    return {"latex_content": PATH_FROM_URI + file_rename}

async def format_to_latex(app_state:AppState) -> AppState:
    experience_info = app_state.experience_info
    projects_info = app_state.projects_info
    header_info = app_state.header_info
    technical_skills_info = app_state.skills_info
    education_info = app_state.education_info
    certifications_info = app_state.certifications_info

    (experience_info, projects_info, header_info,
     technical_skills_info, education_info,
     certifications_info) = await asyncio.gather(
        format_to_latex_agent(
            app_state,
            data=str(experience_info.model_dump()),
            output=type(experience_info)
        ),
        format_to_latex_agent(
            app_state,
            data=str(projects_info.model_dump()),
            output=type(projects_info)
        ),
        format_to_latex_agent(
            app_state,
            data=str(header_info.model_dump()),
            output=type(header_info)
        ),
        format_to_latex_agent(
            app_state,
            data=str(technical_skills_info.model_dump()),
            output=type(technical_skills_info)
        ),
        format_to_latex_agent(
            app_state,
            data=str(education_info.model_dump()),
            output=type(education_info)
        ),
        format_to_latex_agent(
            app_state,
            data=str(certifications_info.model_dump()),
            output=type(certifications_info)
        )
    )

    app_state.experience_info = experience_info
    app_state.projects_info = projects_info
    app_state.header_info = header_info
    app_state.skills_info = technical_skills_info
    app_state.education_info = education_info
    app_state.certifications_info = certifications_info

    return app_state

async  def format_to_latex_agent(app_state:AppState,
                                 data:str,
                                 output:type[BaseModel]) -> type[BaseModel]:
    client_data = app_state.llm_model.get_model()

    data = latex_user_prompt.format(
        json_content=data
    )

    messages = [
        SystemMessage(content=latex_system_message),
        HumanMessage(content=data)
    ]

    structure_llm = client_data.with_structured_output(output)
    print("Formating to latex")
    result = await structure_llm.ainvoke(messages)
    return result


def get_all_tex(app_state:AppState):
    with open("/app/src/utils/templates/template_init.tex", "r", encoding="utf-8") as f:
        template_info = f.read()
    f.close()

    template_info += header_to_latex(app_state)
    template_info += education_to_latex(app_state)
    template_info += work_experience_to_latex(app_state)
    template_info += technical_skills_to_latex(app_state)
    template_info += certifications_to_latex(app_state)
    template_info += projects_to_latex(app_state)

    return template_info

def header_to_latex(app_state:AppState) -> str:

    header = app_state.header_info

    latex = (rf"""

% -------------------- HEADER --------------------
\begin{{center}}
    {{\LARGE \textbf{{{header.name}}}}} \\[6pt]
\end{{center}}
{header.about_me}\\[-2pt]
{header.title} \\[-1pt]
\faPhone\ {header.phone} \quad
\faEnvelope\ \href{{mailto:{header.mail}}}{{{header.mail}}} \quad
\faGithub\ \href{{{header.github}}}{{GitHub}} \quad
\faLinkedin\ \href{{{header.linkedin}}}{{LinkedIn}}

\begin{{center}}
    {header.city}, {header.country}
\end{{center}}
""".strip())

    return latex

def education_to_latex(app_state:AppState) -> str:

    education_field = app_state.education_info

    education_entries = []
    for entry in education_field.education:
        line = (
            rf"\textbf{{{entry.degree}}} — {entry.institution} "
            rf"GPA: {entry.GPA} \hfill {entry.start_date} -- {entry.end_date}"
        )
        education_entries.append(line)

    education_block = "\n\n".join(education_entries)

    courses_block = "\n".join(
        rf"-- {course}\\" for course in education_field.relevant_courses
    )

    latex = (rf"""

% -------------------- EDUCATION --------------------
\section*{{Education}}

{education_block}

\textit{{Relevant Courses:}}
\setlength{{\multicolsep}}{{2pt}}
\begin{{multicols}}{{2}}
\raggedright
{courses_block}
\end{{multicols}}
\vspace{{-10pt}}
""".strip())

    return latex

def work_experience_to_latex(app_state:AppState) -> str:

    work_field = app_state.experience_info

    entries_blocks = []

    for entry in work_field.work_experience:
        responsibilities_block = "\n".join(
            rf"    \item {resp}" for resp in entry.responsibilities
        )

        entry_block = (rf"""

\textbf{{{entry.company}}} \\ 
\textit{{{entry.job_title}}} \hfill {entry.start_date} -- {entry.end_date}
\begin{{itemize}}
{responsibilities_block}
\end{{itemize}}
""".strip())

        entries_blocks.append(entry_block)

    entries_latex = "\n\n".join(entries_blocks)

    latex = (rf"""

% -------------------- WORK EXPERIENCE --------------------
\section*{{Work Experience}}

{entries_latex}

\vspace{{-10pt}}
""".strip())

    return latex

def technical_skills_to_latex(app_state:AppState) -> str:
    skill_field = app_state.skills_info

    skills_block = ", ".join(skill_field.skills)
    languages_block = ", ".join(skill_field.languages)

    latex = rf"""
% -------------------- TECHNICAL SKILLS --------------------
\section*{{Technical Skills}}

\textbf{{Programming:}} {skills_block}

\textbf{{Languages:}} {languages_block}
""".strip()

    return latex


def certifications_to_latex(app_state:AppState) -> str:

    cert_field = app_state.certifications_info

    certifications_block = "\n".join(
        rf"-- {cert}\\" for cert in cert_field.certifications
    )

    latex = (rf"""

% -------------------- CERTIFICATIONS --------------------
\vspace{{-10pt}}
\section*{{Certifications}}

\setlength{{\multicolsep}}{{2pt}}
\begin{{multicols}}{{2}}
\raggedright
{certifications_block}
\end{{multicols}}
\vspace{{-10pt}}
""".strip())

    return latex

def projects_to_latex(
        app_state:AppState,
        closing_text: str | None = "References available upon request",
) -> str:

    projects_field = app_state.projects_info

    project_blocks = []

    for project in projects_field.projects:
        description_items = [
            rf"\item {line}"
            for line in project.description.split("\n")
            if line.strip()
        ]

        if project.technologies_used:
            techs = ", ".join(project.technologies_used)
            description_items.append(rf"\item Technologies used: {techs}")

        items_block = "\n".join(description_items)

        project_block = rf"""
\textbf{{{project.project_name}}}
\begin{{itemize}}
{items_block}
\end{{itemize}}
""".strip()

        project_blocks.append(project_block)

    projects_latex = "\n\n".join(project_blocks)

    closing_block = (
        rf"""
\vfill
\begin{{center}}
{closing_text}
\end{{center}}
""".strip()
        if closing_text
        else ""
    )

    latex = (rf"""
% -------------------- PROJECTS --------------------

\section*{{Relevant Projects}}

{projects_latex}

{closing_block}


% -------------------- END --------------------

\end{{document}}
""".strip())

    return latex
