import gradio as gr

def create_custom_chatbot(tab_title, app_title, app_description, function, additional_inputs=None):
    with gr.Tab(tab_title) as app:
        gr.ChatInterface(
            fn=function,
            title=app_title,
            description=app_description,
            chatbot=gr.Chatbot(height="75vh"),
            fill_width=True,
            fill_height=True,
            additional_inputs=additional_inputs,
            additional_inputs_accordion=gr.Accordion("Configuración del modelo", open=True),
            api_visibility="private"
        )
    return app
