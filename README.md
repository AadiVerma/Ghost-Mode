# Ghost Mode (Server) 👻

Ghost Mode is an AI-powered conversational application that allows users to have a real-time chat with their past selves. By uploading old messaging exports (like WhatsApp chats), the backend uses AI to reconstruct the user's historical behavioral persona—including their tone, recurring phrases, and core beliefs—and brings that persona to life in a dynamic chat interface.

## 🚀 The Pipeline (How It Works)

The Ghost Mode backend is designed around a 4-stage pipeline that processes raw data into a living AI persona.

### 1. Ingestion (Data Parsing)
Users upload a raw chat export file (e.g., WhatsApp `.txt`). The backend parses this file using regular expressions, extracting individual messages, senders, and timestamps. This raw data is efficiently batched and saved to a PostgreSQL database (Supabase). 

### 2. Persona Extraction (AI Analysis)
Once the messages are parsed, the backend triggers an AI Extraction job. Using **Google Gemini 2.5 Flash**, the system analyzes a chronological sample of the user's past messages (filtered by a target age range) and extracts a structured JSON "Persona". This persona includes:
- **Voice Signature**: Tone, punctuation habits, and emoji usage.
- **Recurring Phrases**: The exact slang and idioms they used at that time.
- **Beliefs & Fears**: Core themes they cared about.

### 3. Session Creation
When a user wants to talk to their past self, they create a new Chat Session linked to the extracted Persona. This initializes an empty chat room.

### 4. Chat Exchange (Roleplay)
When the user sends a message, the backend dynamically builds a powerful System Prompt using the extracted Persona JSON. It passes this prompt and the chronological chat history back to Google Gemini. Gemini acts strictly in-character, generating a response that perfectly matches the user's historical voice and tone.

## 🔌 API Endpoints

### `POST /uploads`
Upload a chat export file (e.g., `whatsapp.txt`). Parses the file and stores the raw messages.
- **Request**: `multipart/form-data` with a `file` field.
- **Response**: Returns the `Upload` object and `message_count`.

### `GET /uploads/{id}/messages`
Retrieve the parsed messages for a specific upload.
- **Response**: Array of `Message` objects.

### `POST /personas`
Trigger the AI to extract a persona from an uploaded chat log.
- **Request (JSON)**: `{"upload_id": "<uuid>", "age_range": "17-19"}`
- **Response**: Returns the fully extracted `Persona` object with structured JSON traits.

### `GET /personas/{id}`
Retrieve an extracted persona.

### `POST /sessions`
Initialize a new chat session with a specific persona.
- **Request (JSON)**: `{"persona_id": "<uuid>"}`
- **Response**: Returns the `Session` object.

### `GET /sessions/{id}/messages`
Retrieve the entire chat history for a session.

### `POST /sessions/{id}/messages`
Send a message to the AI persona and receive their reply in real-time.
- **Request (JSON)**: `{"content": "hello there!"}`
- **Response**: Returns the AI's reply as a `SessionMessage` object.

## 🛠 Tech Stack
- **FastAPI**: Asynchronous web framework.
- **SQLAlchemy & Alembic**: Async ORM and database migrations.
- **Supabase (PostgreSQL)**: Database storage, using `JSONB` for flexible AI outputs.
- **Google Gemini 2.5 Flash**: LLM used for both complex JSON data extraction and real-time roleplay chatting.

## 🔑 Setup & Local Development

1. Clone the repository.
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Set up your `.env` file:
   ```env
   DATABASE_URL="postgresql+asyncpg://postgres:[YOUR-PASSWORD]@[YOUR-SUPABASE-HOST]:5432/postgres"
   SECRET_KEY="your-secret-key"
   GEMINI_API_KEY="your-google-gemini-key"
   ```
4. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```
5. Start the development server:
   ```bash
   uv run uvicorn main:app --reload
   ```
