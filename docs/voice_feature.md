# Voice Feature: Run, Test, and Frontend Handoff

This guide covers the current FastAPI → Gemini Live → WebSocket → SQLite voice
pipeline and the browser integration contract.

## 1. Run the backend locally

From the repository root in PowerShell:

1. Copy `.env.example` to `ai_services/.env`.
2. Set `GEMINI_API_KEY` to a Gemini API key enabled for the configured Live
   model. Keep the key on the backend; never put it in frontend code.
3. Install backend requirements (once):

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
   ```

4. Start FastAPI:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
   ```

5. Confirm the server is available:

   ```powershell
   Invoke-RestMethod http://127.0.0.1:8000/health
   ```

   Expected response: `{"status":"ok"}`.

The backend creates `medopsis.db` at the repository root on startup. It creates
the `voice_messages` table automatically. To use a different SQLite file, set
`DATABASE_URI` in `ai_services/.env` to a SQLite URI such as
`sqlite:///./data/medopsis.db`.

## 2. End-to-end pipeline

1. The browser opens `ws://localhost:8000/ws/voice` with `user_id` and
   `conversation_id` query parameters.
2. FastAPI checks the identifiers, enforces one active session per user and
   the global session limit, then opens a Gemini Live session.
3. The server sends a `ready` JSON message after Gemini connects.
4. The browser streams 16 kHz PCM16 mono audio as binary WebSocket frames.
   The backend forwards each frame to Gemini.
5. Gemini response audio is sent to the browser as binary frames. Available
   input/output transcripts and turn completion are sent as JSON messages.
6. Available transcripts are written to SQLite. Closing the WebSocket closes
   the Gemini session and releases the active-session slot.

## 3. WebSocket contract

### Connect

```text
ws://localhost:8000/ws/voice?user_id=<user-id>&conversation_id=<conversation-id>
```

In deployed environments use `wss://`. Both query parameters are required.
`user_id` is currently used for session limits and transcript ownership; this
route does not authenticate or validate the identity. Integrate the project's
authentication before exposing it beyond a trusted development environment.

After a successful Gemini connection, the server sends:

```json
{
  "type": "ready",
  "session_id": "server-generated UUID",
  "input_audio": "pcm16/16000",
  "output_audio": "pcm16/24000"
}
```

### Client messages

| Message | Meaning |
| --- | --- |
| Binary WebSocket frame | Raw PCM16 mono audio at 16,000 Hz; stream chunks as they are captured. |
| `{"type":"audio","data":"<base64>"}` | Same input audio format encoded as base64. Prefer binary frames for streaming. |
| `{"type":"audio_end"}` | Signal the end of the current audio stream to Gemini. |
| `{"type":"text","text":"Hello"}` | Send a text input to the Live session. |
| `{"type":"ping"}` | Request a JSON `pong`. |
| `{"type":"close"}` | Ask the server to close the voice session. |

Use small sequential audio chunks and do not send a WAV/MP3 container header.
Audio passed to the backend should be mono, signed 16-bit PCM, 16 kHz. Browser
microphone audio usually needs down-mixing, resampling, and conversion to
PCM16 before sending.

### Server messages

| Message | Meaning |
| --- | --- |
| Binary WebSocket frame | Raw Gemini output audio, PCM16 at 24,000 Hz. |
| `{"type":"transcript","role":"user","text":"..."}` | Input transcription received from Gemini. |
| `{"type":"transcript","role":"assistant","text":"..."}` | Output transcription received from Gemini. |
| `{"type":"turn_complete"}` | Gemini completed a response turn. |
| `{"type":"pong"}` | Response to `ping`. |
| `{"type":"error","code":"...","message":"..."}` | A connection, validation, or session error. |

Audio and JSON frames share the same WebSocket. The browser must inspect the
message data type: JSON messages are text; audio messages are binary. Configure
the browser socket with `binaryType = "arraybuffer"` (or handle `Blob` frames).
To play output, interpret it as PCM16 at 24 kHz and schedule it through the
Web Audio API; `decodeAudioData()` expects a container format and will not decode
raw PCM frames directly.

### Example: text-only smoke test in a browser

Open the page served by your frontend, then run this in the browser developer
console. Replace the example identifiers as needed:

```javascript
const ws = new WebSocket(
  "ws://localhost:8000/ws/voice?user_id=dev-user&conversation_id=voice-test"
);
ws.binaryType = "arraybuffer";
ws.onmessage = ({ data }) => {
  if (typeof data === "string") {
    console.log("Server:", JSON.parse(data));
  } else {
    console.log("Received PCM audio bytes:", data.byteLength);
  }
};
ws.onopen = () => console.log("WebSocket connected");
ws.onerror = (error) => console.error("WebSocket error:", error);
```

When the server logs a successful Gemini connection and sends `ready`, send:

```javascript
ws.send(JSON.stringify({ type: "text", text: "Hello, can you hear me?" }));
```

Expect a transcript and one or more binary audio frames, followed by
`turn_complete`. Close the connection when finished:

```javascript
ws.send(JSON.stringify({ type: "close" }));
ws.close();
```

This smoke test requires a valid Gemini API key and network access to Gemini.
Without them, the health check can pass but no live voice session can connect.

## 4. Frontend handoff checklist

- Build a WebSocket URL from the API base URL (`ws` for local HTTP, `wss` for
  HTTPS) and URL-encode both identifiers.
- Wait for `ready` before enabling microphone capture or sending text/audio.
- Request microphone permission only after a user action. Stream mono PCM16
  at 16 kHz; use a bounded queue and sequential sends to avoid unbounded
  buffering when the network is slow.
- Handle interleaved JSON and binary messages. Update the transcript UI using
  the `role` field and mark a response complete on `turn_complete`.
- Play binary response audio as PCM16/24 kHz. Queue frames in order to avoid
  gaps; stop playback and release microphone/audio resources when the socket
  closes.
- Send `audio_end` when an utterance ends if the client explicitly manages
  utterance boundaries. Gemini voice activity detection is also configured.
- Handle all `error` codes, socket close/error events, and reconnect only after
  cleaning up the previous socket and audio resources. A user with an active
  session cannot open another one.
- Send `close` for a deliberate stop and close the WebSocket; cleanup also
  occurs when the client disconnects.
- Use the real authenticated user identity when authentication is integrated.
  Do not treat query-string `user_id` as proof of identity.

## 5. Errors and operational notes

| Code | Meaning / client action |
| --- | --- |
| `missing_params` | Supply non-empty `user_id` and `conversation_id`. |
| `session_unavailable` | Session capacity/user limit reached; show a useful message and retry after the previous session ends. |
| `invalid_json` | A text frame was not valid JSON. |
| `invalid_message` | A message field or value was invalid. |
| `unsupported_message` | The `type` is not supported. |
| `session_expired` | The configured maximum session duration was reached. |
| `provider_error` | Gemini or the voice connection failed; check backend logs and API/model configuration. |

The current maximum session duration defaults to 30 minutes and global active
session capacity defaults to 100. The duration limit is checked when the
backend processes incoming WebSocket traffic. Override these values with
`VOICE_SESSION_MAX_DURATION_SECONDS` and `VOICE_MAX_CONCURRENT_SESSIONS`.
HTTP allowed origins are configured with `CORS_ALLOWED_ORIGINS`.

SQLite stores transcript text in `voice_messages` with conversation ID, user
ID, role, content, and creation timestamp. Audio is streamed but not persisted.
Transcripts and conversation identifiers may be sensitive: follow the team's
data-retention and access-control requirements before using real user data.
