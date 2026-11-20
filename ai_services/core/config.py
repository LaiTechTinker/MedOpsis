import os
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import load_dotenv
from dataclasses import dataclass

ai_service_root= Path(__file__).resolve().parents[2]
load_dotenv(ai_service_root / ".env")



def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_origins(value: str) -> tuple[str, ...]:
    return tuple(origin.strip().rstrip("/") for origin in value.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_NAME: str = os.getenv("APP_NAME", "avrum")
    DEBUG: bool = _as_bool(os.getenv("DEBUG"), default=False)
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    JWT_ACCESS_TOKEN_TTL_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_TTL_MINUTES", 60))
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash")
    GEMINI_LIVE_MODEL: str = os.getenv(
        "GEMINI_LIVE_MODEL",
        "gemini-2.5-flash-native-audio-preview-09-2025",
    )
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "qwen/qwen3.8-27b")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")
    VOICE_SYSTEM_INSTRUCTION: str = os.getenv(
        "VOICE_SYSTEM_INSTRUCTION",
        "You are a concise, friendly voice assistant. "
        "Answer clearly, ask clarifying questions when needed, and avoid inventing facts. "
        "Do not present uncertain information as fact.",
    )
 
    DATABASE_URI: str = os.getenv("DATABASE_URI", "sqlite:///./medopsis.db")
    CORS_ALLOWED_ORIGINS: tuple[str, ...] = _parse_origins(
        os.getenv(
            "CORS_ALLOWED_ORIGINS",
            ""
            if APP_ENV.strip().lower() in {"prod", "production"}
            else (
                "http://localhost:5173,http://127.0.0.1:5173,"
                "http://localhost:4173"
            ),
        )
    )
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "MedOPsis")
    VOICE_SESSION_MAX_DURATION_SECONDS: int = int(os.getenv("VOICE_SESSION_MAX_DURATION_SECONDS", 1800))
    VOICE_MAX_CONCURRENT_SESSIONS_PER_USER: int = int(os.getenv("VOICE_MAX_CONCURRENT_SESSIONS_PER_USER", 1))
    VOICE_MAX_CONCURRENT_SESSIONS: int = int(os.getenv("VOICE_MAX_CONCURRENT_SESSIONS", 100))
  
    def __post_init__(self) -> None:
        if self.VOICE_SESSION_MAX_DURATION_SECONDS <= 0:
            raise RuntimeError("VOICE_SESSION_MAX_DURATION_SECONDS must be positive")
        if self.VOICE_MAX_CONCURRENT_SESSIONS_PER_USER != 1:
            raise RuntimeError(
                "VOICE_MAX_CONCURRENT_SESSIONS_PER_USER must be 1"
            )
        if self.VOICE_MAX_CONCURRENT_SESSIONS <= 0:
            raise RuntimeError("VOICE_MAX_CONCURRENT_SESSIONS must be positive")

        if self.APP_ENV.strip().lower() not in {"prod", "production"}:
            return

        errors: list[str] = []
      
        
        if not self.DATABASE_URI.strip():
            errors.append("DATABASE_URI must be set")
        if not self.CORS_ALLOWED_ORIGINS:
            errors.append("CORS_ALLOWED_ORIGINS must list trusted frontend origins")
        elif any(
            origin == "*"
            or (parsed := urlsplit(origin)).scheme != "https"
            or not parsed.netloc
            or parsed.path
            or parsed.query
            or parsed.fragment
            or parsed.username
            or parsed.password
            for origin in self.CORS_ALLOWED_ORIGINS
        ):
            errors.append(
                "CORS_ALLOWED_ORIGINS must contain only explicit HTTPS origins"
            )
        if not any(
            key.strip()
            for key in (
                self.GEMINI_API_KEY,
                self.OPENAI_API_KEY,
                self.GROQ_API_KEY,
            )
        ):
            errors.append(
                "At least one of GEMINI_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY must be set"
            )

        if errors:
            raise RuntimeError(
                "Invalid production configuration: " + "; ".join(errors)
            )

    def require_google_api_key(self) -> str:
        api_key = self.GEMINI_API_KEY.strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required for Google AI operations.")
        return api_key

settings = Settings()