from src.application.models.openai_model import OpenAIModel
from src.application.models.google_gen import GoogleGenModel


models_registry = {
    "OpenAi": OpenAIModel(),
    "Google": GoogleGenModel()
}