from fastapi import FastAPI
from src.gradio_app.app.app import gradio_app
from src.infrastructure.api import router
from gradio import mount_gradio_app

def create_app():
    app = FastAPI(title="CV Generator API", version="1.0.0")
    app.include_router(router, prefix="/api/v1")
    app_gradio = gradio_app()
    mount_gradio_app(app, app_gradio, path="/chat")
    return app
