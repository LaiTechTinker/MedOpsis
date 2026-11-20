import importlib
import importlib.util
import json
from pathlib import Path
import pytest
from fastapi import HTTPException


def knowledge_module():
    assert importlib.util.find_spec("ai_services.chat.knowledge") is not None, "Reference-pack validation is missing"
    return importlib.import_module("ai_services.chat.knowledge")


@pytest.mark.parametrize("change", [None, "pending", "duplicate", "http", "oversized", "invalid_date", "empty", "bad_port"])
def test_reference_pack_validation(monkeypatch, tmp_path, change):
    knowledge = knowledge_module()
    data = json.loads((Path(__file__).parent / "fixtures/synthetic_knowledge.json").read_text())
    if change == "pending": data["approval_status"] = "pending"
    if change == "duplicate": data["sources"] *= 2
    if change == "http": data["sources"][0]["url"] = "http://example.invalid"
    if change == "oversized": data["sources"][0]["text"] = "a" * 3900; data["sources"] += [{**data["sources"][0], "id": "synthetic-2"}]
    if change == "invalid_date": data["reviewed_at"] = "yesterday"
    if change == "empty": data["sources"] = []
    if change == "bad_port": data["sources"][0]["url"] = "https://example.invalid:not-a-port"
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(knowledge, "SOURCE_PATH", path)
    if change is None:
        pack = knowledge.load_knowledge()
        assert pack.sources[0].id == "synthetic-1"
        assert "Software-test fixture only" in pack.context
        assert len(pack.context.encode("utf-8")) <= 4096
    else:
        with pytest.raises(HTTPException) as exc:
            knowledge.load_knowledge()
        assert exc.value.status_code == 503


def test_missing_pack_fails_closed(monkeypatch, tmp_path):
    knowledge = knowledge_module()
    monkeypatch.setattr(knowledge, "SOURCE_PATH", tmp_path / "absent.json")
    with pytest.raises(HTTPException) as exc:
        knowledge.load_knowledge()
    assert exc.value.status_code == 503


def test_oversized_pack_file_fails_closed(monkeypatch, tmp_path):
    knowledge = knowledge_module()
    path = tmp_path / "oversized.json"
    path.write_bytes(b" " * 32769)
    monkeypatch.setattr(knowledge, "SOURCE_PATH", path)
    with pytest.raises(HTTPException) as exc:
        knowledge.load_knowledge()
    assert exc.value.status_code == 503
