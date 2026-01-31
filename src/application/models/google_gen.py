from langchain_google_genai import ChatGoogleGenerativeAI

from src.application.models.base_model import LlmBaseModel

class GoogleGenModel(LlmBaseModel):
    def __init__(self):
        super().__init__()
        self.client = None
        self.models = [
            "gemini-3-flash-preview",
            "gemini-3-pro-preview",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ]

    def start_session(self, model_name: str = "gemini-3-flash-preview", **kwargs):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} is not supported. Available models: {self.models}")

        self.client = ChatGoogleGenerativeAI(
            model=model_name
        )