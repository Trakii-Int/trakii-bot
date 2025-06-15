# TrakiiBot

**TrakiiBot** es un agente conversacional AI que integra la API de Traccar, Telegram (WhatsApp en progreso) y ChatGPT para brindar automatización inteligente en el seguimiento de dispositivos GPS. Responde a consultas sobre ubicación, velocidad y estado de los dispositivos en tiempo real, y además incluye capacidades RAG (búsqueda en base de conocimiento tipo FAQ).

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

Contenido recomendado para `.env`:

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

---

## Indexar la base de conocimiento (RAG)

### Paso 1: Agrega tu archivo de conocimiento

Por defecto, se incluye `faq_trakii.json`, un archivo JSON con respuestas frecuentes. Puedes adaptarlo o reemplazarlo.

Estructura esperada:

```json
[
  { "question": "¿Qué es Trakii?", "answer": "Trakii es una plataforma de rastreo GPS en tiempo real." },
  { "question": "¿Cómo funciona el TrakiiBot?", "answer": "El bot responde a preguntas sobre dispositivos GPS conectados." }
]
```

### Paso 2: Ejecuta el script de indexación

Este comando genera la carpeta `knowledge_db/` persistente:

```bash
python ingest.py
```

> Esto cargará el JSON, fragmentará los textos y los indexará usando embeddings de OpenAI en un vector store local (Chroma).

---

### 🔁 ¿Cómo actualizar la base de conocimiento?

#### a) Si editas el archivo `faq_trakii.json`:

1. Guarda los cambios.
2. Ejecuta nuevamente:

```bash
python ingest.py
```

> Esto sobrescribirá el índice anterior.

#### b) Si agregas un `.txt`, `.md` o `.pdf`:

1. Adapta el script `ingest.py` para usar loaders alternativos (`TextLoader`, `PyPDFLoader`, `UnstructuredPDFLoader`, etc.).
2. Asegúrate de fragmentarlos con `RecursiveCharacterTextSplitter`.
3. Ejecuta `python ingest.py` para reindexar.

---

## Ejecutar el bot

Una vez configurado todo:

```bash
python main.py
```

> Si deseas guardar logs de consola:

```bash
python -u main.py >> logs/terminal.log 2>&1
```

---

## Requisitos

- Python 3.9 o superior
- Acceso a un servidor Traccar con dispositivos configurados
- Token de bot de Telegram desde @BotFather
- Clave de API de OpenAI

---

## Características

- ✅ Ubicación en tiempo real por nombre o ID de dispositivo
- 🚗 Velocidad (conversión de nudos a km/h)
- 🔋 Estado: batería, última conexión, distancia total, movimiento
- 🧠 Modo conversacional con memoria del último dispositivo (en progreso)
- 💬 Consultas generales usando RAG sobre preguntas frecuentes
- 🌐 Soporte multilingüe (español e inglés)
- 🔒 Acceso restringido por ID de usuario Telegram
- 📜 Logs rotados automáticamente

---

## Arquitectura

- `main.py`: manejador de mensajes Telegram
- `my_trakii_agent.py`: lógica del agente LangGraph
- `prompts.py`: sistema de prompts de clasificación
- `ingest.py`: indexación de base de conocimiento para RAG
- `faq_trakii.json`: base de conocimiento usada por el bot
- `logs/`: carpeta para logs del bot y errores

---

## Contacto

¿Tienes preguntas o sugerencias? 📬 [carlossalva.mendivill@gmail.com](mailto\:carlossalva.mendivill@gmail.com)

