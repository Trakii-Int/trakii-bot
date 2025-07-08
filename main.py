import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from log_config import bot_logger, error_logger
from my_trakii_agent import agent  # Agente LangGraph

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Diccionario de usuarios autorizados y credenciales Traccar
USER_CREDENTIALS = {
    7434126358: {
        "username": os.getenv("TRACCAR_USER_7434126358"),
        "password": os.getenv("TRACCAR_PASS_7434126358"),
    },
    289677525: {
        "username": os.getenv("TRACCAR_USER_289677525"),
        "password": os.getenv("TRACCAR_PASS_289677525"),
    },
    # Agrega más usuarios según sea necesario
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    if user_id not in USER_CREDENTIALS:
        await update.message.reply_text("❌ Acceso no autorizado. Contacta con el administrador.")
        return

    # Extrae credenciales del usuario
    credentials = USER_CREDENTIALS[user_id]
    traccar_username = credentials["username"]
    traccar_password = credentials["password"]

    bot_logger.info(f"[INPUT] UserID: {user_id} - Message: {user_text}")

    state_input = {"user_input": {"message": user_text}}

    # Configuración personalizada para LangGraph Agent
    config = {
        "configurable": {
            "langgraph_user_id": f"telegram-{user_id}",
            "traccar_username": traccar_username,
            "traccar_password": traccar_password,
        }
    }

    try:
        result = agent.invoke(state_input, config=config)
        response = "⚠️ Sin respuesta."
        for message in result["messages"]:
            if hasattr(message, "content"):
                response = message.content

        bot_logger.info(f"[OUTPUT] UserID: {user_id} - Triage & Response: {response}")
        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        error_logger.error(f"❌ Error en handle_message: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ha ocurrido un error inesperado. Por favor intenta más tarde.")

# Comando /start
async def start(update, context):
    greeting = "¡Hola! 😊 Soy *TrakiiBot*, tu asistente de rastreo GPS."
    capabilities = (
        "Puedo ayudarte con:\n"
        "- 📍 Ubicación\n"
        "- 🚗 Velocidad\n"
        "- 🔋 Estado (batería, movimiento, distancia)\n"
        "- 📋 Listar dispositivos\n\n"
        "¿Qué necesitas hoy?"
    )
    await update.message.reply_markdown(f"{greeting}\n\n{capabilities}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 TrakiiBot está corriendo...")
    app.run_polling()
