import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from log_config import bot_logger, error_logger
import requests

# LangGraph Agent
from my_trakii_agent import agent  
config = {"configurable": {"langgraph_user_id": "telegram-user"}} 

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

AUTHORIZED_USERS = [7434126358, 289677525, 6779730126, 551723663]
# Manejar mensajes normales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()  # 🧼 Elimina espacios innecesarios

    # Verifica si el usuario está autorizado
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Acceso no autorizado. Contacta con el administrador.")
        return

    # Log de entrada del usuario
    bot_logger.info(f"[INPUT] UserID: {user_id} - Message: {user_text}")

    state_input = {"user_input": {"message": user_text}}

    try:
        # Ejecutar el agente de LangGraph
        result = agent.invoke(state_input, config=config)
        response = "⚠️ Sin respuesta."
        for message in result["messages"]:
            if hasattr(message, "content"):
                response = message.content  # guarda el último válido

        # Log de salida del agente
        bot_logger.info(f"[OUTPUT] UserID: {user_id} - Triage & Response: {response}")

        # Respuesta al usuario
        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        # Log de error y respuesta al usuario
        error_logger.error(f"❌ Error en handle_message: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ha ocurrido un error inesperado. Por favor intenta más tarde.")

# Comando /start
#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.message.reply_text("¡Hola! Soy TrakiiBot. Puedes preguntarme por la ubicación, velocidad o estado de tus dispositivos.")
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
