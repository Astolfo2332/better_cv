import gradio as gr

from src.domain.request_models import Request
from src.gradio_app.app.utils.gradio_customs import create_custom_chatbot
from src.gradio_app.app.domain.app_state import AppState
from src.gradio_app.interfaces.app_interface import get_available_models_interface, get_available_vendors_interface, \
    process_interface, re_do_latex_interface

DEFAULT_LANG="Español"
DEFAULT_JSON_TEMPLATE='{\n  "clave": "valor"\n}'

def gradio_app():

    app_state = gr.State(AppState(
        response_language=DEFAULT_LANG,
        json_template=DEFAULT_JSON_TEMPLATE
    ))

    vendors = get_available_vendors_interface()
    vendor_dropdown = gr.Dropdown(
        choices=vendors,
        label="Proveedor del Modelo de Lenguaje",
        value=""
    )

    model_dropdown = gr.Dropdown(
        label="Modelo de Lenguaje",
    )

    language_dropdown = gr.Dropdown(
        choices=["Español", "English"],
        label="Idioma de Respuesta",
        value=DEFAULT_LANG
    )

    with gr.Blocks(fill_height=True) as app:
        accordion = gr.Accordion("Configuración del Modelo de Lenguaje", open=True)
        with accordion:
            gr.Markdown("### Selecciona el Proveedor y Modelo de Lenguaje")
            vendor_dropdown.render()
            model_dropdown.render()
            language_dropdown.render()

    #Encontrar este workaround para que la interfaz se vea en toda la pantalla fue un dolor de cabeza UnU
    # Selectores para el Chat
        with gr.Tab("Chat Interface"):
            gr.ChatInterface(
                fn=chat_logic,
                title="Chatbot de Generación de CV",
                description="Interactúa con el modelo de lenguaje para generar contenido basado en la información proporcionada.",
                chatbot=gr.Chatbot(height="75vh"),
                fill_width=True,
                fill_height=True,
                api_visibility="private",
                additional_inputs=[app_state]
            )

        with gr.Tab("JSON Template Config"):
            gr.Markdown("### Configuración del Template JSON")
            gr.Markdown("Edita aquí el formato JSON que utilizará el chatbot. Los cambios se reflejarán automáticamente en el chat.")
            json_input = gr.Code(
                language="json",
                label="Estructura JSON (Template)",
                value=DEFAULT_JSON_TEMPLATE,
                lines=15,
                interactive=True
            )

        with gr.Tab("Reprocesar TEX"):
            gr.Markdown("### Reprocesar Documentos TEX")
            gr.ChatInterface(
                fn=re_do_latex_chat,
                title="Reprocesar Documentos TEX",
                description="Sube un documento TEX para que sea reprocesado",
                chatbot=gr.Chatbot(height="75vh"),
                fill_width=True,
                fill_height=True,
                api_visibility="private"
            )

        # Logica de actualización de modelos según el vendor seleccionado

        vendor_dropdown.change(
            fn=change_vendor_models,
            inputs=[vendor_dropdown],
            outputs=[model_dropdown]
        ).then(
            fn=update_provider,
            inputs=[vendor_dropdown, app_state],
            outputs=[app_state]
        )
        model_dropdown.change(
            fn=update_model,
            inputs=[model_dropdown, app_state],
            outputs=[app_state]
        )
        language_dropdown.change(
            fn=update_language,
            inputs=[language_dropdown, app_state],
            outputs=[app_state]
        )

        json_input.input(
            fn=update_json_template,
            inputs=[json_input, app_state],
            outputs=[app_state]
        )

        json_input.change(
            fn=update_json_template,
            inputs=[json_input, app_state],
            outputs=[app_state]
        )

    return app

async def chat_logic(message, history, app_state):
    app_state.job_offer = message
    response = await process_interface(app_state)
    response = response.get("response")
    if response is None:
        response = "Lo siento, no pude generar una respuesta en este momento."
        return response

    return f"Descarga el documento generado: [Aquí]({response}) UwU"

async def re_do_latex_chat(message, history):
    response = await re_do_latex_interface(message)
    response = response.get("response")
    if response is None:
        response = "Lo siento, no pude procesar el documento TEX en este momento."
    else:
        response = f"Descarga el documento reprocesado: [Aquí]({response}) OwO"
    return response

def change_vendor_models(vendor_name):
    models = get_available_models_interface(vendor_name)
    return gr.update(choices=models, value=models[0] if models else None)

def update_provider(provider, state):
    state.llm_provider = provider
    return state

def update_model(model, state):
    state.llm_model = model
    return state

def update_language(lang, state):
    state.response_language = lang
    return state

def update_json_template(json_val, state):
    state.json_template = json_val
    return state