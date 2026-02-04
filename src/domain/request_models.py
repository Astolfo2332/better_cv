from pydantic import BaseModel

class Request(BaseModel):
    job_offer:str
    json_template:str
    llm_vendor: str
    model: str
    response_language:str


class ReProcessTexRequest(BaseModel):
    new_tex : str