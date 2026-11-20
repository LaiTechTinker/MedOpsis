from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Callable
from typing import Any

from ai_services.core.config import settings
from google import genai
from google.genai import types


logger = logging.getLogger(__name__)


class Gemini_Voice_Service:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = (api_key or settings.GEMINI_API_KEY).strip()
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is required for Gemini Live sessions.")
        self.model = model or settings.GEMINI_LIVE_MODEL
        self.client = genai.Client(api_key=self.api_key)
        self.session_cm: Any | None = None #session context manager manages the opening and closing of the session
        self.session: Any | None = None  #this stores the active connection between my app and gemini

    @property
    def config(self) -> dict[str, Any]:
        return {
            "response_modalities": ["AUDIO"],
            "system_instruction": settings.VOICE_SYSTEM_INSTRUCTION,
            "input_audio_transcription": {},
            "output_audio_transcription": {},
            "realtime_input_config": {
                "automatic_activity_detection": {
                    "disabled": False,
                    "prefix_padding_ms": 20,
                    "silence_duration_ms": 600,
                }
            },
        }
    async def connect(self,):
        if self.session is not None:
           return self.session
        self.session_cm=self.client.aio.live.connect(
            model=self.model,
            config=self.config
        )
        self.session = await self.session_cm.__aenter__()
        logger.info("Connected Gemini Live session using model %s", self.model)
        return self.session
    async def close(self) -> None:
        if self.session_cm is not None:
            try:
                await self.session_cm.__aexit__(None, None, None)
            finally:
                self.session = None
                self.session_cm = None
    async def send_audio(self, chunk: bytes) -> None:
        if self.session is None:
            raise RuntimeError("Gemini Live session is not connected.")

        await self.session.send_realtime_input(
            audio=types.Blob(
                data=chunk,
                mime_type="audio/pcm;rate=16000",
            )
        )
    async def send_text(self, text: str) -> None:
        if self.session is None:
            raise RuntimeError("Gemini Live session is not connected.")

        await self.session.send_realtime_input(text=text)

    # this code block is a signal for sending end of audio stream to the Gemini Live session, indicating that no more audio data will be sent. This is important for the model to know when to finalize its response based on the received audio input.
    async def send_audio_stream_end(self) -> None:
        if self.session is None:
            raise RuntimeError("Gemini Live session is not connected.")

        await self.session.send_realtime_input(audio_stream_end=True)

    async def receive_audio(self, handler: Callable[[bytes], Any]) -> None:
        if self.session is None:
            raise RuntimeError("Gemini Live session is not connected.")

        async for response in self.session.receive():
            if not getattr(response, "server_content", None):
                continue

            model_turn = getattr(response.server_content, "model_turn", None)
            if not model_turn:
                continue

            for part in getattr(model_turn, "parts", []) or []:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and getattr(inline_data, "data", None):
                    await handler(inline_data.data)

    async def receive_events(self) -> AsyncIterator[Any]:
        session = self.session
        if session is None:
            raise RuntimeError("Gemini Live session is not connected.")

        async for event in session.receive():
            yield event






       
