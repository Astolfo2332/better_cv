from langchain_core.messages import SystemMessage, HumanMessage

from src.domain.orq_models import AppState
from src.application.agents.prompts.education_prompts import education_system_message, education_user_prompt
from src.domain.cv_models import EducationField

async def education_agent(appstate:AppState) -> dict:

    client_data = appstate.llm_model.get_model()

    education_data = appstate.personal_json.get("education")
    rel_courses = appstate.personal_json.get("relevant_courses")

    if not education_data or not rel_courses:
        raise ValueError("Must provide educational data")

    education_data_compose = education_user_prompt.format(
        language=appstate.language_to_respond,
        personal_info=str(education_data) + str(rel_courses),
        pos_info=appstate.postulation_info
    )

    messages = [
        SystemMessage(content=education_system_message),
        HumanMessage(content=education_data_compose)
    ]

    structure_llm = client_data.with_structured_output(EducationField)
    print("Formating educational info")
    results = await structure_llm.ainvoke(messages)
    return {"education_info": results}
