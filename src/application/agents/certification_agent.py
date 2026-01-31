from langchain_core.messages import SystemMessage, HumanMessage

from src.domain.orq_models import AppState
from src.application.agents.prompts.technical_prompts import technical_system_message, technical_user_prompt
from src.domain.cv_models import CertificationsField

async def cert_agent(appstate:AppState) -> dict:

    client_data = appstate.llm_model.get_model()

    cert_data = appstate.personal_json.get("certifications")
    if not cert_data:
        raise ValueError("Must provide certification data")

    tech_data_compose = technical_user_prompt.format(
        language=appstate.language_to_respond,
        personal_info=cert_data,
        pos_info=appstate.postulation_info
    )

    messages = [
        SystemMessage(content=technical_system_message),
        HumanMessage(content=tech_data_compose)
    ]

    structure_llm = client_data.with_structured_output(CertificationsField)
    print("Formating certification info")
    response = await structure_llm.ainvoke(messages)
    return {"certifications_info": response}
