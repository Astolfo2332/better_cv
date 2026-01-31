from src.application.agents.header_agent import header_agent
from src.application.agents.certification_agent import cert_agent
from src.application.agents.education_agent import education_agent
from src.application.agents.projects_agent import projects_agent
from src.application.agents.technical_agent import tech_agent
from src.application.agents.work_exp_agent import work_agent
from src.application.agents.latex_agent import latex_agent
from src.application.agents.validator_agent import validator_agent

from src.domain.orq_models import AppState
import asyncio

async def parallel_research_node(state: AppState) -> dict:
    print("--- Ejecutando investigaciones en paralelo ---")

    results = await asyncio.gather(
        header_agent(state),
        education_agent(state),
        work_agent(state),
        tech_agent(state),
        cert_agent(state),
        projects_agent(state)
    )

    combined_update = {}
    for result in results:
        if result:
            combined_update.update(result)

    print("--- Toda la data recolectada ---")
    return combined_update

async def orchestrator(app_state: AppState) -> dict:
    print("Iniciando orquestador de agentes...")


    collected_data = await parallel_research_node(app_state)

    app_state = app_state.model_copy(update=collected_data)

    latex_result = await latex_agent(app_state)

    #TODO: agregar validador

    print("Orquestador ha completado su ejecución.")
    return {"response": latex_result.get("latex_content")}


def save_workflow_diagram(app, file_name="agent_flow.png"):
    import os

    file_path = os.path.join("/app", "src", "domain", file_name)
    try:
        png_bytes = app.get_graph().draw_mermaid_png()
        with open(file_path, "wb") as f:
            f.write(png_bytes)
        print(f"Diagrama guardado exitosamente en: {file_path}")
    except Exception as e:
        print(f"Error al guardar el diagrama: {e}")

if __name__ == "__main__":
    from src.domain.orq_models import AppState
    from src.domain.request_models import Request
    from src.application.models.model_registry import models_registry
    import json
    import asyncio
    import os
    from dotenv import load_dotenv
    load_dotenv()

    main = os.getcwd()

    with open(main + "/src/utils/templates/json_example.json", "r", encoding="utf-8") as f:
        personal_json = json.load(f)

    request = Request(
        llm_vendor="Google",
        model="gemini-3-flash-preview",
        job_offer="Descripción completa del empleo: El Servicio de Empleo operado por Comfama es la plataforma que conecta a las personas con empresas de diversos sectores ubicadas en Medellín y Antioquia; las vacantes corresponden a oportunidades laborales ofrecidas por estas empresas y pueden consultarse en [www.comfama.com](http://www.comfama.com) en la opción “Trabaja con nosotros”; empresa aliada busca tecnólogo/a y/o profesional en sistemas con un (1) año de experiencia en desarrollo de software y cargos afines, cuya misión será diseñar, desarrollar, probar y mantener soluciones de software que respondan a las necesidades del negocio garantizando calidad, eficiencia y escalabilidad mediante buenas prácticas de programación, metodologías ágiles y herramientas modernas en colaboración con equipos multidisciplinarios; funciones: diseñar y desarrollar aplicaciones web y/o de software según requerimientos funcionales y técnicos, implementar y ejecutar pruebas unitarias y de integración para asegurar estabilidad y calidad, gestionar versiones de código fuente con Git siguiendo lineamientos del equipo, participar en comités de Infraestructura y Arquitectura aportando al análisis y toma de decisiones técnicas bajo supervisión senior, investigar y proponer nuevas tecnologías, herramientas y buenas prácticas para la mejora continua; conocimientos técnicos: Javascript, Typescript, control de versiones Git y metodologías ágiles, deseable Docker, NestJS y Java; competencias laborales: comunicación asertiva, pensamiento lógico y trabajo en equipo; salario entre $3.000.000 y $3.300.000 más prestaciones de ley; horario acordado con la empresa; tipo de contrato fijo; lugar de trabajo Medellín; requisitos: ser tecnólogo/a o profesional con 1 año de experiencia; condiciones de la oferta: sueldo neto mensual $3.000.000.",
        json_template="nada",
        response_language="Spanish"
    )

    llm = models_registry.get(request.llm_vendor)
    llm.start_session(request.model)

    app_state = AppState(
        llm_model=llm,
        language_to_respond=request.response_language,
        # personal_json=json.loads(request.json_template),
        personal_json=personal_json,
        postulation_info=request.job_offer
    )

    result = asyncio.run(orchestrator(app_state))
    print(result)
