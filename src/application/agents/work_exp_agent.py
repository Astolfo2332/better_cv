from langchain_core.messages import SystemMessage, HumanMessage

from src.domain.orq_models import AppState
from src.application.agents.prompts.work_prompts import work_system_message, work_user_prompt
from src.domain.cv_models import WorkExperienceField

async def work_agent(appstate:AppState) -> dict:

    client_data = appstate.llm_model.get_model()

    work_data = appstate.personal_json.get("work_experience")
    if not work_data:
        raise ValueError("Must provide work data")

    work_data_compose = work_user_prompt.format(
        language=appstate.language_to_respond,
        personal_info=work_data,
        pos_info=appstate.postulation_info
    )

    messages = [
        SystemMessage(content=work_system_message),
        HumanMessage(content=work_data_compose)
    ]

    structure_llm = client_data.with_structured_output(WorkExperienceField)
    print("Formating work experience info")
    result = await structure_llm.ainvoke(messages)

    return {"experience_info": result}
