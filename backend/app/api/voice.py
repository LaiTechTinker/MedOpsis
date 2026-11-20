from __future__ import annotations

import asyncio
import base64
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

try:
    from app.database import save_voice_message
except ModuleNotFoundError:
    from backend.app.database import save_voice_message
from ai_services.voice.gemini_service import Gemini_Voice_Service
from ai_services.voice.voice_session_service import VoiceSessionManager
from ai_services.core.config import settings

logger=logging.getLogger(__name__)
router=APIRouter(tags=["voice"])
VOICE_CLEANUP_TIMEOUT_SECONDS = 5


def get_voice_session_manager(app) ->VoiceSessionManager:
    manager= getattr(app.state, "voice_session_manager", None)
    if manager is None:
        manager = VoiceSessionManager(
            max_sessions=settings.VOICE_MAX_CONCURRENT_SESSIONS,
            max_duration_seconds=settings.VOICE_SESSION_MAX_DURATION_SECONDS,
        )
        app.state.voice_session_manager = manager
    return manager


def _content_from_event(event: object) -> tuple[list[bytes], str | None, str | None]:
    audio_chunks: list[bytes] = []
    input_text: str | None = None
    output_text: str | None = None

    server_content = getattr(event, "server_content", None)
    if server_content is None:
        return audio_chunks, input_text, output_text

    input_transcription = getattr(server_content, "input_transcription", None)
    if input_transcription is not None:
        input_text = getattr(input_transcription, "text", None)

    output_transcription = getattr(server_content, "output_transcription", None)
    if output_transcription is not None:
        output_text = getattr(output_transcription, "text", None)

    model_turn = getattr(server_content, "model_turn", None)
    if model_turn is not None:
        for part in getattr(model_turn, "parts", []) or []:
            inline_data = getattr(part, "inline_data", None)
            data = getattr(inline_data, "data", None) if inline_data else None
            if data:
                audio_chunks.append(data if isinstance(data, bytes) else bytes(data))

    return audio_chunks, input_text, output_text


@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket) -> None:
    user_id = websocket.query_params.get("user_id", "").strip()
    conversation_id = websocket.query_params.get("conversation_id", "").strip()
    await websocket.accept()

    if not user_id or not conversation_id:
        await websocket.send_json({
            "type": "error",
            "code": "missing_params",
            "message": "user_id and conversation_id query parameters are required.",
        })
        await websocket.close(code=1008)
        return

    manager = get_voice_session_manager(websocket.app)
    try:
        session = manager.create_session(user_id, conversation_id)
    except ValueError as exc:
        await websocket.send_json({
            "type": "error",
            "code": "session_unavailable",
            "message": str(exc),
        })
        await websocket.close(code=1008)
        return

    provider = Gemini_Voice_Service()
    session.provider_session = provider

    try:
        await provider.connect()
        await websocket.send_json({
            "type": "ready",
            "session_id": session.session_id,
            "input_audio": "pcm16/16000",
            "output_audio": "pcm16/24000",
        })

        async def receive_from_gemini() -> None:
            async for event in provider.receive_events():
                if not session.active:
                    break

                audio_chunks, input_text, output_text = _content_from_event(event)
                for chunk in audio_chunks:
                    await websocket.send_bytes(chunk)

                if input_text:
                    await websocket.send_json({"type": "transcript", "role": "user", "text": input_text})
                    await save_voice_message(conversation_id, user_id, "user", input_text)

                if output_text:
                    await websocket.send_json({"type": "transcript", "role": "assistant", "text": output_text})
                    await save_voice_message(conversation_id, user_id, "assistant", output_text)

                server_content = getattr(event, "server_content", None)
                if getattr(server_content, "turn_complete", False):
                    await websocket.send_json({"type": "turn_complete"})

        provider_task = asyncio.create_task(receive_from_gemini())
        session.provider_task = provider_task

        while session.active:
            if manager.is_expired(session.session_id):
                await websocket.send_json({
                    "type": "error",
                    "code": "session_expired",
                    "message": "The voice session reached its maximum duration.",
                })
                break
            message = await websocket.receive()
            session.last_activity_at = datetime.now(timezone.utc)

            if message["type"] == "websocket.disconnect":
                break

            if "bytes" in message:
                await provider.send_audio(message["bytes"])
                continue

            if "text" not in message:
                continue

            try:
                payload = json.loads(message["text"])
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "code": "invalid_json",
                    "message": "Expected a JSON control message.",
                })
                continue

            message_type = payload.get("type")
            if message_type == "audio":
                encoded = payload.get("data")
                if not isinstance(encoded, str):
                    raise ValueError("audio data must be a base64 string")
                await provider.send_audio(base64.b64decode(encoded))
            elif message_type == "text":
                text = payload.get("text")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("text must be a non-empty string")
                await provider.send_text(text.strip())
                await save_voice_message(conversation_id, user_id, "user", text.strip())
            elif message_type == "audio_end":
                await provider.send_audio_stream_end()
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif message_type == "close":
                break
            else:
                await websocket.send_json({
                    "type": "error",
                    "code": "unsupported_message",
                    "message": f"Unsupported message type: {message_type}",
                })
    except WebSocketDisconnect:
        logger.info("Voice websocket disconnected: %s", session.session_id)
    except ValueError as exc:
        await websocket.send_json({
            "type": "error",
            "code": "invalid_message",
            "message": str(exc),
        })
    except Exception:
        logger.exception("Voice websocket failed: %s", session.session_id)
        try:
            await websocket.send_json({
                "type": "error",
                "code": "provider_error",
                "message": "The voice provider connection failed.",
            })
        except Exception:
            pass
    finally:
        session.active = False
        provider_task = getattr(session, "provider_task", None)
        if provider_task is not None:
            provider_task.cancel()
            await asyncio.gather(provider_task, return_exceptions=True)
        await provider.close()
        manager.close_session(session.session_id)
    
   