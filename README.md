MedOpsis Voice Backend
========================

FastAPI backend for real-time speech-to-speech communication with Gemini Live.

Setup
-----

1. Copy `.env.example` to `ai_services/.env`.
2. Set `GEMINI_API_KEY`.
3. Install dependencies:
   `.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt`
4. Start the server from the repository root:
   `.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`

WebSocket
---------

Connect to:

`ws://127.0.0.1:8000/ws/voice?user_id=USER&conversation_id=CONVERSATION`

Send raw 16 kHz PCM16 audio bytes, or JSON control messages:

- `{"type":"text","text":"Hello"}`
- `{"type":"audio","data":"<base64-pcm16>"}` (16 kHz)
- `{"type":"audio_end"}`
- `{"type":"ping"}`
- `{"type":"close"}`

Gemini audio is returned as binary 24 kHz PCM16 frames. Text transcripts are returned as JSON.
SQLite voice transcripts are stored in `medopsis.db`.