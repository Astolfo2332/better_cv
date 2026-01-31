from langchain_core.messages import SystemMessage, HumanMessage

from src.domain.orq_models import AppState
from src.application.agents.prompts.projects_prompts import projects_system_message, projects_user_prompt
from src.domain.cv_models import ProjectsField

async def projects_agent(appstate:AppState) -> dict:

    client_data = appstate.llm_model.get_model()

    projects_data = appstate.personal_json.get("projects")
    if not projects_data:
        raise ValueError("Must provide projects data")

    project_data_compose = projects_user_prompt.format(
        language=appstate.language_to_respond,
        personal_info=projects_data,
        pos_info=appstate.postulation_info
    )

    messages = [
        SystemMessage(content=projects_system_message),
        HumanMessage(content=project_data_compose)
    ]

    structure_llm = client_data.with_structured_output(ProjectsField)
    print("Formating projects info")

    result = await structure_llm.ainvoke(messages)
    return {"projects_info": result}
