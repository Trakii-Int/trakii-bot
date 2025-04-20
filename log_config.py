import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Asegúrate de que exista la carpeta "logs"
os.makedirs("logs", exist_ok=True)

# === Logger para actividad general del bot ===
bot_logger = logging.getLogger("TrakiiBot")
bot_logger.setLevel(logging.INFO)

bot_handler = TimedRotatingFileHandler(
    filename="logs/trakii-bot.log",
    when="midnight",
    interval=30,
    backupCount=12,
    encoding="utf-8"
)
bot_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
bot_logger.addHandler(bot_handler)

# === Logger para errores ===
error_logger = logging.getLogger("TrakiiErrors")
error_logger.setLevel(logging.ERROR)

error_handler = TimedRotatingFileHandler(
    filename="logs/errors.log",
    when="midnight",
    interval=30,
    backupCount=12,
    encoding="utf-8"
)
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
error_logger.addHandler(error_handler)
