from src.domain.request_models import Request, ReProcessTexRequest
from src.gradio_app.app.domain.app_state import AppState
from src.infrastructure.api import get_available_models, get_available_vendors, process, re_process_tex


def get_available_models_interface(vendor_name: str):
    return get_available_models(vendor_name).get("available_models", [])


def get_available_vendors_interface():
    return get_available_vendors().get("available_vendors", [])


async def process_interface(app_state:AppState):
    request = Request(
        job_offer=app_state.job_offer,
        json_template=app_state.json_template,
        llm_vendor=app_state.llm_provider,
        model=app_state.llm_model,
        response_language=app_state.response_language
    )
    return await process(request)


async def re_do_latex_interface(response: str) -> dict:
     try:
            request = ReProcessTexRequest(new_tex=response)
            return await re_process_tex(request)
     except Exception as e:
            return {"response": f"[ERROR] {str(e)}"}