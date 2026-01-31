from langchain_core.messages import SystemMessage, HumanMessage

from src.domain.orq_models import AppState
from src.application.agents.prompts.technical_prompts import technical_system_message, technical_user_prompt
from src.domain.cv_models import SkillSetField

async def tech_agent(appstate:AppState) -> dict:

    client_data = appstate.llm_model.get_model()

    tech_data = appstate.personal_json.get("technical_skills")
    if not tech_data:
        raise ValueError("Must provide tech data")

    tech_data_compose = technical_user_prompt.format(
        language=appstate.language_to_respond,
        personal_info=tech_data,
        pos_info=appstate.postulation_info
    )

    messages = [
        SystemMessage(content=technical_system_message),
        HumanMessage(content=tech_data_compose)
    ]

    structure_llm = client_data.with_structured_output(SkillSetField)
    print("Formating tech skills info")

    result = await structure_llm.ainvoke(messages)
    return {"skills_info":result}
