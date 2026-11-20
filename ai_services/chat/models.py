from typing import Annotated, Literal
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StrictStr, model_validator
from pydantic_core import PydanticCustomError


def nonblank(value: str) -> str:
    if value.isspace():
        raise ValueError("Text must not be blank")
    return value


Text = Annotated[StrictStr, Field(min_length=1, max_length=4000), AfterValidator(nonblank)]


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    role: Literal["user", "assistant"]
    content: Text


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    language: Literal["en", "yo", "ig", "ha"]
    messages: list[Message] = Field(min_length=1, max_length=16)
    screening_report: Text | None = None

    @model_validator(mode="after")
    def validate_context(self):
        if self.messages[-1].role != "user":
            raise ValueError("The final message must be from the user")
        size = sum(len(message.content.encode("utf-8")) for message in self.messages)
        size += len((self.screening_report or "").encode("utf-8"))
        if size > 8192:
            raise PydanticCustomError("content_too_large", "Conversation content exceeds the limit")
        return self
