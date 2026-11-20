import json
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StrictStr, ValidationError
from starlette.concurrency import run_in_threadpool
from ai_services.chat import auth, knowledge, provider
from ai_services.chat.models import ChatRequest, nonblank

app = FastAPI(title="MedOpsis text chat", debug=False)
security = HTTPBearer(auto_error=False)


class PublicReference(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: StrictStr
    title: StrictStr
    url: StrictStr


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    answer: Annotated[StrictStr, Field(min_length=1, max_length=8000), AfterValidator(nonblank)]
    references: list[PublicReference] = Field(max_length=8)


def require_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    if credentials is None:
        raise HTTPException(401, detail={"code": "authentication_required", "message": "An application bearer token is required."})
    return auth.authorize_token(credentials.credentials)


request_schema = ChatRequest.model_json_schema()
# shortcut: one referenced input type; expand this if more input models are added.
request_schema["properties"]["messages"]["items"] = request_schema.pop("$defs")["Message"]


@app.post("/chat", response_model=ChatResponse, openapi_extra={"requestBody": {"required": True, "content": {"application/json": {"schema": request_schema}}}})
async def chat(request: Request, user: str = Depends(require_user)):
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > 16384:
            raise HTTPException(413, detail={"code": "body_too_large", "message": "The request body exceeds the limit."})
        raw.extend(chunk)
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(400, detail={"code": "invalid_json", "message": "The request must contain valid JSON."}) from None
    try:
        payload = ChatRequest.model_validate(data)
    except ValidationError as exc:
        oversized = any(error["type"] == "content_too_large" for error in exc.errors())
        raise HTTPException(413 if oversized else 422, detail={"code": "content_too_large" if oversized else "invalid_request", "message": "Conversation content exceeds the limit." if oversized else "The request fields are invalid."}) from None
    pack = knowledge.load_knowledge()
    return await run_in_threadpool(provider.generate_reply, payload, pack)
