import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from joblens.extraction import JobPosting, extract_job

CASES = json.loads((Path(__file__).resolve().parents[1] / "data/examples.json").read_text(encoding="utf-8"))


class StubClient:
    def __init__(self, output):
        self.output = output

    def generate(self, system, user, schema=None):
        return json.dumps(self.output, ensure_ascii=False)


@pytest.mark.parametrize("case", CASES)
def test_schema_and_grounding_with_missing_fields(case):
    job = extract_job(case["text"], StubClient(case["expected"]))
    assert job.model_dump() == case["expected"]


def test_hallucinated_skill_is_rejected():
    expected = dict(CASES[0]["expected"])
    expected["required_skills"] = [{"name": "Kubernetes", "evidence": "Required: Kubernetes"}]
    with pytest.raises(ValueError, match="Kubernetes"):
        extract_job(CASES[0]["text"], StubClient(expected))


def test_hallucinated_salary_is_rejected():
    expected = {**CASES[1]["expected"], "salary": "100 million VND"}
    with pytest.raises(ValueError, match="salary"):
        extract_job(CASES[1]["text"], StubClient(expected))


def test_invalid_json_schema_is_rejected():
    with pytest.raises(ValidationError):
        JobPosting.model_validate({"job_title": 123, "unexpected": True})


@pytest.mark.parametrize("text", [" ", "x" * 25001])
def test_invalid_input_does_not_call_model(text):
    with pytest.raises(ValueError):
        extract_job(text, None)
