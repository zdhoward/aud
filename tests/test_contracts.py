import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from aud import AudioMetadata, Dir, NamingProfile, cli, json_document, json_schema
from aud.core.operations.files import Copy
from aud.core.progress import ProgressEvent
from aud.core.results import BatchResult, FileResult

CORPUS = json.loads(
    (Path(__file__).parents[1] / "conformance/v1/cases.json").read_text(encoding="utf-8")
)


@pytest.fixture(scope="module")
def validator():
    schema = json_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def portable(value, root):
    if isinstance(value, str) and value.startswith(str(root)):
        return "$ROOT" + value[len(str(root)) :].replace("\\", "/")
    if isinstance(value, dict):
        return {key: portable(item, root) for key, item in value.items()}
    if isinstance(value, list):
        return [portable(item, root) for item in value]
    return value


def test_copy_matches_portable_corpus(tmp_path, validator):
    case = CORPUS["copy"]
    source = tmp_path / case["input_name"]
    source.write_bytes(case["input_text"].encode())
    d = Dir(tmp_path, extensions=["flac"])
    plan = d.plan().add(Copy(tmp_path / "out"))
    preview = json_document("preview", d.preview(plan))
    assert portable(preview, tmp_path) == case["preview"]
    validator.validate(preview)
    result = json_document("result", d.execute(plan))
    assert portable(result, tmp_path) == case["result"]
    validator.validate(result)
    assert (tmp_path / "out" / source.name).read_bytes() == source.read_bytes()


@pytest.mark.parametrize("case", CORPUS["naming"])
def test_naming_matches_corpus(case):
    assert (
        NamingProfile(**case["profile"])
        .render(AudioMetadata(**case["metadata"]), case["extension"])
        .as_posix()
        == case["expected"]
    )


@pytest.mark.parametrize("case", CORPUS["results"])
def test_result_semantics_match_corpus(case, validator):
    result = BatchResult(
        [FileResult("input", "output", "Copy", status) for status in case["statuses"]]
    )
    assert result.succeeded is case["succeeded"]
    validator.validate(json_document("result", result))


def test_progress_and_error_golden_documents(validator):
    expected = CORPUS["progress"]
    assert json_document("progress", ProgressEvent(**expected["payload"])) == expected
    validator.validate(expected)
    validator.validate(CORPUS["error"])


@pytest.mark.parametrize(
    "change",
    [
        lambda doc: doc.update(schema_version=2),
        lambda doc: doc.update(kind="unknown"),
        lambda doc: doc.update(extra=True),
        lambda doc: doc["payload"].update(succeeded=True),
        lambda doc: doc["payload"]["items"][0].update(status="invented"),
        lambda doc: doc["payload"]["items"][0].pop("target"),
    ],
)
def test_schema_rejects_contract_drift(change, validator):
    doc = json_document("result", BatchResult([FileResult("in", "out", "Copy", "failed")]))
    change(doc)
    with pytest.raises(ValidationError):
        validator.validate(doc)


def test_document_is_snapshot_and_legacy_dict_is_unchanged():
    result = BatchResult([FileResult("in", "out", "Copy", "success", details={"values": [1]})])
    before = copy.deepcopy(result.to_dict())
    document = json_document("result", result)
    document["payload"]["items"][0]["details"]["values"].append(2)
    assert result.to_dict() == before
    assert set(before) == {"succeeded", "items"}
    schema = json_schema()
    schema.clear()
    assert json_schema()["$defs"]
    with pytest.raises(ValueError):
        json_document("result", {}, version=True)
    with pytest.raises(ValueError):
        json_document("unknown", {})
    with pytest.raises(ValueError):
        json_document("result", {"value": float("nan")})


@pytest.mark.parametrize("command", ["list", "inspect", "convert", "album"])
def test_versioned_cli_documents_match_schema(command, populated_dir, capsys, validator):
    args = [
        command,
        str(populated_dir),
        "--extensions",
        "wav",
        "--pattern",
        "bloop.*",
        "--json",
        "--json-version",
        "1",
    ]
    if command == "convert":
        args += ["--format", "flac", "--dry-run"]
    if command == "album":
        config = populated_dir / "album.json"
        config.write_text(json.dumps({"release": {"title": "Album", "artist": "Artist"}}))
        args += ["--config", str(config), "--target", str(populated_dir / "album.zip"), "--dry-run"]
    assert cli.run(args) == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["schema_version"] == 1
    validator.validate(doc)


def test_versioned_cli_execution_and_error(populated_dir, capsys, validator):
    args = [
        "convert",
        str(populated_dir),
        "--extensions",
        "wav",
        "--pattern",
        "bloop.*",
        "--format",
        "flac",
        "--json",
        "--json-version",
        "1",
    ]
    assert cli.run(args) == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["kind"] == "result"
    validator.validate(doc)
    assert cli.run(args) == 1
    doc = json.loads(capsys.readouterr().out)
    assert doc["kind"] == "error"
    validator.validate(doc)


def test_version_requires_machine_output(populated_dir, capsys):
    assert cli.run(["list", str(populated_dir), "--json-version", "1"]) == 2
    assert "requires --json" in capsys.readouterr().err
