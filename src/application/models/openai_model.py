from langchain_openai import ChatOpenAI

from src.application.models.base_model import LlmBaseModel

class OpenAIModel(LlmBaseModel):
    def __init__(self):
        super().__init__()
        self.client = None
        self.models = [
            "gpt-5.2",
            "gpt-5.1",
            "gpt-4.1",
        ]

    def start_session(self, model_name: str = "gpt-5.2", **kwargs):
        reasoning = None
        if "reasoning" in kwargs:
            reasoning = kwargs["reasoning"]
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} is not supported. Available models: {self.models}")

        self.client = ChatOpenAI(
            model=model_name,
            reasoning_effort="medium" if reasoning is None else reasoning
        )