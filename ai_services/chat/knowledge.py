import json
from datetime import date
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlsplit
from fastapi import HTTPException
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator, model_validator
from .models import Text, nonblank

SOURCE_PATH = Path(__file__).resolve().parents[1] / "medical_knowledge" / "references.json"
Label = Annotated[StrictStr, Field(min_length=1, max_length=200), AfterValidator(nonblank)]


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: Annotated[StrictStr, Field(min_length=1, max_length=64), AfterValidator(nonblank)]
    title: Label
    url: Annotated[StrictStr, Field(min_length=1, max_length=2000)]
    text: Text

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        parsed = urlsplit(value)
        # urlsplit checks port syntax/range only when this property is read.
        _ = parsed.port
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Source URLs must use HTTPS without credentials")
        return value


class KnowledgePack(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    version: Label
    approval_status: Literal["approved"]
    reviewed_by: Label
    reviewed_at: StrictStr
    sources: list[Source] = Field(min_length=1, max_length=8)

    @field_validator("reviewed_at")
    @classmethod
    def validate_review_date(cls, value):
        date.fromisoformat(value)
        return value

    @property
    def context(self):
        return json.dumps([{"id": s.id, "title": s.title, "text": s.text} for s in self.sources], ensure_ascii=False, separators=(",", ":"))

    @model_validator(mode="after")
    def validate_sources(self):
        if len({s.id for s in self.sources}) != len(self.sources):
            raise ValueError("Reference IDs must be unique")
        if len(self.context.encode("utf-8")) > 4096:
            raise ValueError("Reference context exceeds the limit")
        return self


def load_knowledge() -> KnowledgePack:
    try:
        with SOURCE_PATH.open("rb") as source:
            data = source.read(32769)
        if len(data) > 32768:
            raise ValueError("Reference file exceeds the limit")
        return KnowledgePack.model_validate_json(data)
    except (OSError, ValueError, ValidationError):
        raise HTTPException(503, detail={"code": "knowledge_unavailable", "message": "An approved medical reference pack is required."}) from None
