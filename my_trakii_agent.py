import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dotenv import load_dotenv

from typing_extensions import TypedDict, Literal, Annotated
from pydantic import BaseModel, Field

from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.store.memory import InMemoryStore

from log_config import bot_logger, error_logger

from prompts import triage_system_prompt, triage_user_prompt

# === Load environment variables ===
_ = load_dotenv()

TRACCAR_URL = os.getenv("TRACCAR_URL")
#TRACCAR_USERNAME = os.getenv("TRACCAR_USERNAME")
#TRACCAR_PASSWORD = os.getenv("TRACCAR_PASSWORD")

# === Agent profile and prompt instructions ===
profile = {
    "name": "TrakiiBot",
    "full_name": "AI TrakiiBot",
    "user_profile_background": (
        "Agente conversacional AI avanzado que integra ChatGPT, la API de WhatsApp y la API de GPS de Trakki. "
        "Automatiza consultas y tareas frecuentes, optimiza tiempos mediante aprendizaje automático (RAG) "
        "y reduce la necesidad de múltiples licencias de software. Conecta fácilmente con otras soluciones tecnológicas, "
        "mejorando la eficiencia operativa y la experiencia del cliente. Puntos importantes: automatización y ahorro de tiempo, "
        "reducción de costos operativos, integración tecnológica eficiente, y atención 24/7 para una mejor experiencia del cliente."
    )
}

prompt_instructions = {
    "triage_rules": {
        "location": "When the user asks about GPS coordinates, location, where the device is, or any synonym for the above on English or Spanish.",
        "speed": "When the user asks about how fast the device is going, current speed, or any synonym for the above on English or Spanish.",
        "status": "When the user asks whether the device is online, the battery level, last time it reported data, or any synonym for the above on English or Spanish.",
        "list": "When the user asks to list all devices, see available GPS trackers, or get a catalog of registered units.",
        "ask": "When the user asks general questions (Who is Trakii, what can you do, how does it work?).",
        "ignore": "If the message is not related to location, speed or status.",  
    },
    "agent_instructions": "Classify incoming Telegram messages into the correct type of request for a GPS tracking system.",
}

# === LangGraph memory and model setup ===
store = InMemoryStore(index={"embed": "openai:text-embedding-3-small"})
llm = init_chat_model("openai:gpt-4o-mini")

# Configura RAG
vectordb = Chroma(persist_directory="knowledge_db", embedding_function=OpenAIEmbeddings())
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectordb.as_retriever())

class Router(BaseModel):
    reasoning: str = Field(description="Step-by-step reasoning behind the classification.")
    classification: Literal["location", "speed", "status", "list", "ask", "ignore"] = Field(description="The type of query requested by the user")

llm_router = llm.with_structured_output(Router)

class State(TypedDict):
    user_input: dict
    messages: Annotated[list, add_messages]

# === Routing function ===
def triage_router(state: State, config, store) -> Command[Literal["handle_location", "handle_speed", "handle_status", "handle_list", "handle_ask", "handle_ignore"]]:
    message = state['user_input']['message']
    langgraph_user_id = config['configurable']['langgraph_user_id']

    rules = prompt_instructions["triage_rules"]

    system_prompt = triage_system_prompt.format(
        full_name=profile["full_name"],
        user_profile_background=profile["user_profile_background"],
        triage_location=rules["location"],
        triage_speed=rules["speed"],
        triage_status=rules["status"],
        triage_list=rules["list"],
        triage_ask=rules["ask"],
        triage_no=rules["ignore"],
        name=profile["name"],
        examples=None,
    )
    user_prompt = triage_user_prompt.format(message=message)

    result = llm_router.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ])

    print(f"🧠 Reasoning: {result.reasoning}")
    print(f"📦 Classified as: {result.classification}")
    bot_logger.info(f"[TRIAGE] Clasificación: {result.classification}")
    return Command(
        goto=f"handle_{result.classification}",
        update={"messages": [{"role": "user", "content": message}]}
    )

# === 🛰️ Handler functions ===

def handle_location(state: State, config):
    print("📍 Handling location query...")
    user_message = state["messages"][-1].content.lower()

 # 🔐 Obtén credenciales personalizadas desde el config
    traccar_username = config["configurable"].get("traccar_username")
    traccar_password = config["configurable"].get("traccar_password")

    if not traccar_username or not traccar_password:
        return {"messages": [{"role": "assistant", "content": "⚠️ No se configuraron credenciales para Traccar."}]}

    
    try:
        devices = requests.get(
            f"{TRACCAR_URL}/api/devices",
            auth=HTTPBasicAuth(traccar_username, traccar_password)
        ).json()

        matched_device = next((d for d in devices if d["name"].lower() in user_message or str(d["id"]) in user_message), None)

        if not matched_device:
            content = "No pude encontrar un dispositivo que coincida con tu mensaje."
        else:
            position = requests.get(
                f"{TRACCAR_URL}/api/positions/?id={matched_device['positionId']}",
                auth=HTTPBasicAuth(traccar_username, traccar_password)
            ).json()[0]

            latitude = position["latitude"]
            longitude = position["longitude"]

            content = (
                f"📍 Ubicación del dispositivo '{matched_device['name']}':\n"
                f"Latitud: {latitude}, Longitud: {longitude}\n"
                f"[Ver en Google Maps](https://www.google.com/maps?q={latitude},{longitude})"
            )
    except Exception as e:
        print("❌ Error:", e)
        content = "Error al obtener la ubicación del dispositivo."

    return {"messages": [{"role": "assistant", "content": content}]}

def handle_speed(state: State, config):
    print("🚗 Handling speed query...")
    user_message = state["messages"][-1].content.lower()
 # 🔐 Obtén credenciales personalizadas desde el config
    traccar_username = config["configurable"].get("traccar_username")
    traccar_password = config["configurable"].get("traccar_password")

    if not traccar_username or not traccar_password:
        return {"messages": [{"role": "assistant", "content": "⚠️ No se configuraron credenciales para Traccar."}]}

    
    try:
        devices = requests.get(
            f"{TRACCAR_URL}/api/devices",
            auth=HTTPBasicAuth(traccar_username, traccar_password)
        ).json()

        matched_device = next((d for d in devices if d["name"].lower() in user_message or str(d["id"]) in user_message), None)

        if not matched_device:
            content = "No encontré un dispositivo que coincida con tu mensaje."
        else:
            position = requests.get(
                f"{TRACCAR_URL}/api/positions/?id={matched_device['positionId']}",
                auth=HTTPBasicAuth(traccar_username, traccar_password)
            ).json()[0]

            speed_kph = round(position["speed"] * 1.852, 1)
            content = f"🚗 El dispositivo '{matched_device['name']}' se mueve a {speed_kph} km/h."
    except Exception as e:
        print("❌ Error:", e)
        content = "Error al obtener la velocidad del dispositivo."

    return {"messages": [{"role": "assistant", "content": content}]}

def handle_status(state: State, config):
    print("🔋 Handling status query...")
    user_message = state["messages"][-1].content.lower()

     # 🔐 Obtén credenciales personalizadas desde el config
    traccar_username = config["configurable"].get("traccar_username")
    traccar_password = config["configurable"].get("traccar_password")

    if not traccar_username or not traccar_password:
        return {"messages": [{"role": "assistant", "content": "⚠️ No se configuraron credenciales para Traccar."}]}

    

    try:
        devices = requests.get(
            f"{TRACCAR_URL}/api/devices",
            auth=HTTPBasicAuth(traccar_username, traccar_password)
        ).json()

        matched_device = next((d for d in devices if d["name"].lower() in user_message or str(d["id"]) in user_message), None)

        if not matched_device:
            content = "No encontré un dispositivo que coincida con tu mensaje."
        else:
            position = requests.get(
                f"{TRACCAR_URL}/api/positions/?id={matched_device['positionId']}",
                auth=HTTPBasicAuth(traccar_username, traccar_password)
            ).json()[0]

            attributes = position.get("attributes", {})
            battery_level = attributes.get("batteryLevel", "No disponible")
            battery = attributes.get("battery", "No disponible")
            total_distance = round(attributes.get("totalDistance", 0) / 1000, 2)

            fix_time = position.get("fixTime")
            motion = attributes.get("motion", False)
            motion_status = "🟢 En movimiento" if motion else "🔴 Detenido"

            fix_time_str = (
                datetime.fromisoformat(fix_time.replace("Z", "+00:00")).strftime("%m/%d/%Y, %I:%M:%S %p")
                if fix_time else "No disponible"
            )

            content = (
                f"📡 Estado del dispositivo '{matched_device['name']}':\n"
                f"```\n"
                f"🕒 Fix Time               {fix_time_str}\n"
                f"📍 Distancia              {total_distance} km\n"
                f"🔋 Nivel de la batería    {battery_level}%\n"
                f"🔋 Voltaje de la batería  {battery} V\n"
                f"🚗 Movimiento             {motion_status}\n"
                f"```"
            )
    except Exception as e:
        print("❌ Error:", e)
        content = "Error al obtener el estado del dispositivo."

    return {"messages": [{"role": "assistant", "content": content}]}

def handle_list(state: State, config):
    print("📋 Handling list devices query...")

     # 🔐 Obtén credenciales personalizadas desde el config
    traccar_username = config["configurable"].get("traccar_username")
    traccar_password = config["configurable"].get("traccar_password")

    if not traccar_username or not traccar_password:
        return {"messages": [{"role": "assistant", "content": "⚠️ No se configuraron credenciales para Traccar."}]}

    

    try:
        response = requests.get(
            f"{TRACCAR_URL}/api/devices",
            auth=HTTPBasicAuth(traccar_username, traccar_password)
        )
        response.raise_for_status()
        devices = response.json()

        if not devices:
            content = "No se encontraron dispositivos registrados."
        else:
            lines = ["📋 Lista de dispositivos registrados:"]
            for d in devices:
                lines.append(f"- {d['name']} (ID: {d['id']})")
            content = "\n".join(lines)

    except Exception as e:
        print("❌ Error:", e)
        content = "Ocurrió un error al obtener la lista de dispositivos."

    return {
        "messages": [
            {"role": "assistant", "content": content}
        ]
    }

def handle_ask(state: State):
    user_text = state["messages"][-1].content
    try:
        answer = qa_chain.run(user_text)
        content = answer
    except Exception as e:
        error_logger.error(f"RAG error: {e}", exc_info=True)
        content = "Lo siento, no pude recuperar esa información ahora."
    return {"messages":[{"role":"assistant","content":content}]}
    
def handle_ignore(state: State):
    print("🚫 Handling ignored query...")
    return {"messages": [{"role": "assistant", "content": "Lo siento, no entendí tu consulta. Puedes preguntarme por la ubicación, velocidad o estado de un dispositivo."}]}

# === 🧩 Build LangGraph ===
agent_graph = StateGraph(State)
agent_graph.add_node("triage_router", triage_router)
agent_graph.add_node("handle_location", handle_location)
agent_graph.add_node("handle_speed", handle_speed)
agent_graph.add_node("handle_status", handle_status)
agent_graph.add_node("handle_list", handle_list)
agent_graph.add_node("handle_ask", handle_ask)
agent_graph.add_node("handle_ignore", handle_ignore)

agent_graph.add_edge(START, "triage_router")
agent_graph.add_edge("handle_location", END)
agent_graph.add_edge("handle_speed", END)
agent_graph.add_edge("handle_status", END)
agent_graph.add_edge("handle_list", END)
agent_graph.add_edge("handle_ask", END)
agent_graph.add_edge("handle_ignore", END)

agent = agent_graph.compile()
