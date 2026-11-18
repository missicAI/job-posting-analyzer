import json
from pathlib import Path

from dotenv import load_dotenv

from joblens.extraction import extract_job
from joblens.llm import LLMClient

ROOT = Path(__file__).resolve().parent


def main():
    load_dotenv(ROOT / ".env")
    cases = json.loads((ROOT / "data/examples.json").read_text(encoding="utf-8"))
    client = LLMClient.from_env()
    results = []
    for case in cases:
        try:
            actual = extract_job(case["text"], client).model_dump()
            expected = case["expected"]
            fields = ["job_title", "company", "location", "work_mode", "experience", "salary"]
            scalar_score = sum(actual[f] == expected[f] for f in fields) / len(fields)
            skill_scores = {}
            for field in ["required_skills", "preferred_skills"]:
                predicted = {s["name"].casefold() for s in actual[field]}
                gold = {s["name"].casefold() for s in expected[field]}
                skill_scores[field + "_f1"] = (
                    2 * len(predicted & gold) / (len(predicted) + len(gold)) if predicted or gold else 1.0
                )
            results.append(
                {
                    "name": case["name"],
                    "valid_and_grounded": True,
                    "scalar_exact_match": scalar_score,
                    **skill_scores,
                    "output": actual,
                }
            )
        except (ValueError, RuntimeError) as exc:
            results.append({"name": case["name"], "valid_and_grounded": False, "error": str(exc)})
    report = {
        "provider": client.provider,
        "model": client.model,
        "cases": results,
        "note": "Three hand-written development cases; not a representative benchmark. Failures are included in the valid rate.",
        "valid_rate": sum(r["valid_and_grounded"] for r in results) / len(results),
    }
    out = ROOT / "reports/llm_evaluation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(r["valid_and_grounded"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
