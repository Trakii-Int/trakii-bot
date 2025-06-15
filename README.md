# TrakiiBot

**TrakiiBot** es un agente conversacional AI que integra la API de Traccar, Telegram (WhatsApp en progreso) y ChatGPT para brindar automatización inteligente en el seguimiento de dispositivos GPS. Responde a consultas sobre ubicación, velocidad, estado y preguntas frecuentes en tiempo real mediante RAG (Retrieval-Augmented Generation).

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
OPENAI_API_KEY=your_openai_api_key
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

Para guardar la salida (incluidos los logs y errores):

```bash
python main.py > output.log 2>&1
```

## Requisitos

* Python 3.9 o superior
* Acceso a un servidor Traccar con dispositivos configurados
* Token de bot de Telegram desde @BotFather
* Cuenta OpenAI con clave API habilitada

## Características

* ✅ Ubicación en tiempo real por nombre o ID de dispositivo
* ✅ Velocidad del dispositivo (conversión automática de nudos a km/h)
* ✅ Estado: batería, última conexión, distancia total, movimiento
* ✅ Memoria del último dispositivo consultado (en desarrollo)
* ✅ Modo conversación natural por Telegram (español e inglés)
* ✅ Registro en logs rotativos (actividad y errores)
* ✅ RAG: integración con preguntas frecuentes desde el sitio de Trakii

## Actualizar información RAG

El sistema RAG utiliza una base de conocimiento indexada a partir del sitio web [https://www.trakii.co/faq](https://www.trakii.co/faq).

Para actualizar la información:

1. Extrae el contenido actualizado del sitio y guárdalo en un archivo `.md` o `.txt` en el directorio `knowledge_base/`
2. Ejecuta el script de carga para generar los vectores y persistirlos:

```bash
python ingest.py  # Este script se encargará de actualizar knowledge_db/
```

3. Reinicia el bot para cargar los cambios.

## Arquitectura

* `main.py`: manejador de mensajes de Telegram, logging y autorización
* `my_trakii_agent.py`: lógica del agente, clasificación, handlers y conexión a RAG
* `prompts.py`: sistema de prompts para clasificación LangChain
* `logs/`: carpeta donde se almacenan logs rotativos de actividad y errores
* `knowledge_base/`: documentos base utilizados para responder mediante RAG
* `knowledge_db/`: base de vectores persistente usada por el motor de búsqueda semántica

## Contacto

¿Tienes preguntas o sugerencias?
¡Abrí un issue o escríbenos a [carlossalva.mendivill@gmail.com](mailto:carlossalva.mendivill@gmail.com)
