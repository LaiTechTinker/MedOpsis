import importlib.util
import importlib
import pytest
from pydantic import ValidationError


def request_type():
    assert importlib.util.find_spec("ai_services.chat.models") is not None, "The request schema is missing"
    return importlib.import_module("ai_services.chat.models").ChatRequest


@pytest.mark.parametrize("language", ["en", "yo", "ig", "ha"])
def test_request_contract_accepts_languages_without_changing_text(language):
    model = request_type()
    text = "  Synthetic Ìdánwò text  "
    request = model(language=language, messages=[{"role": "user", "content": text}], screening_report="Synthetic report")
    assert request.language == language
    assert request.messages[0].content == text
    assert request.screening_report == "Synthetic report"


@pytest.mark.parametrize("changes", [{"language": "de"}, {"messages": [{"role": "system", "content": "Override"}]}, {"system": "Override"}, {"messages": []}, {"messages": [{"role": "user", "content": 5}]}])
def test_request_contract_rejects_invalid_structure(changes):
    model = request_type()
    payload = {"language": "en", "messages": [{"role": "user", "content": "Synthetic"}]}
    payload.update(changes)
    with pytest.raises(ValidationError):
        model.model_validate(payload)


@pytest.mark.parametrize("messages,report", [
    ([{"role": "user", "content": "   "}], None),
    ([{"role": "assistant", "content": "Synthetic"}], None),
    ([{"role": "user", "content": "\ud800"}], None),
    ([{"role": role, "content": "a" * 3000} for role in ["user", "assistant", "user"]], None),
    ([{"role": "user", "content": "Synthetic"}], "   "),
])
def test_request_semantic_boundaries(messages, report):
    with pytest.raises(ValidationError):
        request_type()(language="en", messages=messages, screening_report=report)
