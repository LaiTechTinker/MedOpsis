from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
import time
from uuid import uuid4

from ai_services.voice.gemini_service import Gemini_Voice_Service


@dataclass
class VoiceSession:
    session_id: str
    user_id: str
    conversation_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at_monotonic: float = 0 
    active: bool = True
    provider_session: Gemini_Voice_Service| None = None
    provider_task: asyncio.Task | None = None


class VoiceSessionManager:
    def __init__(
        self,
        max_sessions: int = 100,
        max_duration_seconds: int = 1800,
    ) -> None:
        if max_sessions <= 0:
            raise ValueError("max_sessions must be positive")
        if max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be positive")
        self.max_sessions = max_sessions
        self.max_duration_seconds = max_duration_seconds
        self._sessions_by_id: dict[str, VoiceSession] = {}
        self._sessions_by_user: dict[str, VoiceSession] = {}

    def create_session(self, user_id: str, conversation_id: str) -> VoiceSession:
        if user_id in self._sessions_by_user:
            raise ValueError("User already has an active voice session.")
        if len(self._sessions_by_id) >= self.max_sessions:
            raise ValueError("Voice session capacity has been reached.")

        session = VoiceSession(
            session_id=str(uuid4()),
            user_id=user_id,
            conversation_id=conversation_id,
            expires_at_monotonic=time.monotonic() + self.max_duration_seconds,
        )

        self._sessions_by_id[session.session_id] = session
        self._sessions_by_user[user_id] = session
        return session

    def get_session(self, session_id: str) -> VoiceSession | None:
        return self._sessions_by_id.get(session_id)

    def get_active_session_for_user(self, user_id: str) -> VoiceSession | None:
        return self._sessions_by_user.get(user_id)

    def is_expired(self, session_id: str) -> bool:
        session = self._sessions_by_id.get(session_id)
        if session is None:
            return True
        if time.monotonic() >= session.expires_at_monotonic:
            self.close_session(session_id)
            return True
        return False

    def close_session(self, session_id: str) -> bool:
        session = self._sessions_by_id.get(session_id)
        if session is None:
            return False

        session.active = False
        self._sessions_by_id.pop(session_id, None)
        if self._sessions_by_user.get(session.user_id) is session:
            self._sessions_by_user.pop(session.user_id, None)
        return True
