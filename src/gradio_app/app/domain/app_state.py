from pydantic import BaseModel

class AppState(BaseModel):
    llm_provider: str = ""
    llm_model: str = ""
    json_template: str = ""
    job_offer: str = ""
    response_language: str = ""