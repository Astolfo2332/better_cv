from langchain_core.language_models.llms import BaseLLM

class LlmBaseModel:
    def __init__(self):
        self.client:BaseLLM = None
        self.models = []

    def start_session(self, model_name: str):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_available_models(self):
        return self.models

    def get_model(self):
        if not self.client:
            raise ValueError("Model session has not been started. Call start_session() first.")
        return self.client
