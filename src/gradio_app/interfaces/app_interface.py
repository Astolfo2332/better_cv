from src.domain.request_models import Request
from src.infrastructure.api import get_available_models, get_available_vendors, process

def get_available_models_interface(vendor_name: str):
    return get_available_models(vendor_name).get("available_models", [])


def get_available_vendors_interface():
    return get_available_vendors().get("available_vendors", [])

async def process_interface(request:Request):
    return await process(request)