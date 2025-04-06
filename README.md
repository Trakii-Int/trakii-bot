# TrakiiBot

**TrakiiBot** es un agente conversacional AI que integra la API de Traccar, Telegram (WhatsApp en progreso) y ChatGPT para brindar automatización inteligente en el seguimiento de dispositivos GPS. Responde a consultas sobre ubicación, velocidad y estado de los dispositivos en tiempo real.

---

## Instalación

Sigue los pasos a continuación para clonar y ejecutar el proyecto localmente:

### 1. Clona el repositorio
```bash
git clone https://github.com/Trakii-Int/trakii-bot.git
cd trakii-bot/
```

### 2. Crea el archivo de configuración
```bash
nano .env
```

Contenido recomendado para .env:
```env
TRACCAR_URL=https://your-traccar-server/
TRACCAR_USERNAME=your_username
TRACCAR_PASSWORD=your_password
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_bot_token
```

### 3. (Opcional) Instala venv si no está instalado
```bash
sudo apt install python3.11-venv
```
### 4. Crea y activa el entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Actualiza pip e instala dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
## Ejecutar el bot

Una vez configurado, simplemente ejecuta:

```bash
python main.py
```

## Requisitos
	•	Python 3.9 o superior
	•	Acceso a un servidor Traccar con dispositivos configurados
	•	Token de bot de Telegram desde @BotFather


## Características
	•	Ubicación en tiempo real por nombre o ID de dispositivo
	•	Velocidad del dispositivo (conversión automática de nudos a km/h)
	•	Estado: batería, última conexión, distancia total, movimiento
	•	Memoria del último dispositivo consultado (en desarrollo)
	•	Modo conversación natural por Telegram (español e inglés)

## Arquitectura
	•	main.py: manejador de mensajes de Telegram
	•	my_trakii_agent.py: lógica de clasificación y consultas al API de Traccar
	•	prompts.py: sistema de prompts para LangChain

## Contacto

¿Tienes preguntas o sugerencias?
¡Abrí un issue o escríbenos a carlossalva.mendivill@gmail.com
