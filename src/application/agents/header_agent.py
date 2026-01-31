from langchain_core.messages import SystemMessage, HumanMessage

from src.domain.orq_models import AppState
from src.application.agents.prompts.header_prompts import header_system_message, header_user_prompt
from src.domain.cv_models import Header

async def header_agent(appstate:AppState) -> dict:

    client_data = appstate.llm_model.get_model()

    header_data = appstate.personal_json.get("header")
    if not header_data:
        raise ValueError("Must provide Header data")

    header_data_compose = header_user_prompt.format(
        language=appstate.language_to_respond,
        personal_info=str(header_data),
        pos_info=appstate.postulation_info
    )

    messages = [
        SystemMessage(content=header_system_message),
        HumanMessage(content=header_data_compose)
    ]

    structure_llm = client_data.with_structured_output(Header)
    print("Formating header info")
    result = await structure_llm.ainvoke(messages)
    return {"header_info": result}


