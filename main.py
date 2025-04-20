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

AUTHORIZED_USERS = [7434126358, 289677525, 6779730126]
# Manejar mensajes normales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Acceso no autorizado. Contacta con el administrador.")
        return
  
    user_text = update.message.text
    bot_logger.info(f"[INPUT] UserID: {user_id} - Message: {user_text}")
 
    state_input = {
        "user_input": {"message": user_text}
    }

#    try:
#        
#        result = agent.invoke(state_input, config=config)
#        response = ""
#
#        
#        for m in result["messages"]:
#            if hasattr(m, "content"):
#                
#                response = m.content
#                bot_logger.info(f"[OUTPUT] Triage & Response: {response}")
#                await update.message.reply_text(response, parse_mode="Markdown")
#                break
#
#    except Exception as e:
#        error_logger.error(f"❌ Error en handle_message: {e}", exc_info=True)
#        await update.message.reply_text("Ha ocurrido un error inesperado.")


    result = agent.invoke(state_input, config=config)

    # Obtener última respuesta del agente
    response = ""
    for m in result["messages"]:
        if hasattr(m, "content"):
            response = m.content

    print(f"🤖 Respuesta: {response}")
    await update.message.reply_text(response, parse_mode="Markdown")



# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy TrakiiBot. Puedes preguntarme por la ubicación, velocidad o estado de tus dispositivos.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 TrakiiBot está corriendo...")
    app.run_polling()
