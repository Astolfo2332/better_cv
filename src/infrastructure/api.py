from fastapi import FastAPI, HTTPException, APIRouter
import json
from dotenv import load_dotenv

from src.application.agents.latex_agent import re_do_latex
from src.application.orquestrator.graph_orq import orchestrator
from src.domain.orq_models import AppState
from src.domain.request_models import Request, ReProcessTexRequest
from src.application.models.model_registry import models_registry

import os
from fastapi.responses import FileResponse

load_dotenv()

router = APIRouter()


@router.post("/process")
async def process(request: Request):
    """Endpoint para procesar la solicitud de generación de CV"""

    if request.llm_vendor not in models_registry.keys():
        HTTPException(status_code=400, detail=f"Model not available try:"
                                              f" {models_registry[request.llm_vendor].get_available_models()}")

    llm = models_registry.get(request.llm_vendor)
    llm.start_session(request.model)

    try:
        json_data = json.loads(request.json_template)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON template: {str(e)}")

    app_state = AppState(
        llm_model=llm,
        language_to_respond=request.response_language,
        personal_json=json_data,
        postulation_info=request.job_offer
    )

    try:
        result = await orchestrator(app_state)
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.post("/re_process_tex")
async def re_process_tex(request: ReProcessTexRequest):
    return re_do_latex(request.new_tex)


@router.get("available_vendors")
def get_available_vendors():
    """Endpoint para obtener los vendors disponibles"""
    return {"available_vendors": list(models_registry.keys())}


@router.get("/available_models/{vendor_name}")
def get_available_models(vendor_name: str):
    """Endpoint para obtener los modelos disponibles de un vendor"""
    if vendor_name not in models_registry.keys():
        raise HTTPException(status_code=400, detail=f"Model not available try:"
                                                  f" {models_registry.keys()}")
    llm = models_registry.get(vendor_name)
    return {"available_models": llm.get_available_models()}


@router.get("/download_file/{file_name}")
def download_file(file_name: str):
    """Endpoint para descargar un archivo generado"""

    file_path = os.path.join("/app", "src", "outputs", file_name)
    print("download file path:", file_path)

    if not file_name.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files can be downloaded")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=file_name, media_type='application/zip')