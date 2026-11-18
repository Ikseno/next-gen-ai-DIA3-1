#!/usr/bin/env python3
"""TD 2: run synthetic votes or compare panels on stored traces.

No network, no key. Single-question mode uses three distinct model families.
The five-model comparison includes both GPT-OSS variants, so it is a quorum of
five measured models, not five independent model families. References are
compared AFTER the decision: the vote never receives them.

    python3 atelier-vote.py                                    # four synthetic examples
    python3 atelier-vote.py --traces traces-td1.csv --case C02  # the real traces of one question
    python3 atelier-vote.py --traces traces-td1.csv --compare   # 2-of-3 vs 3-of-5, all questions
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

PANEL = [
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
]

PANEL_FIVE = [
    ("groq", "openai/gpt-oss-120b"),
    ("groq", "openai/gpt-oss-20b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
    ("openrouter", "dots-studio/dots-3-note-preview:free"),
]


def load_vote():
    spec = importlib.util.spec_from_file_location("student_skeleton", Path(__file__).with_name("skeleton-multi-llm-en.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def proposals_for(rows, case, nature, panel=PANEL):
    """Fixed panel: an unavailable member keeps its place but casts no vote.

    The last CSV row per panel member is its last attempt. Use one chronological
    export per experiment; reject mixed experiments rather than merging them.
    References and correctness verdicts are not passed to the student's vote.
    """
    selected = {}
    for row in rows:
        key = (row["provider"], row["model_requested"])
        if row["case_id"] == case and row["nature"] == nature and key in panel:
            selected[key] = row
    proposals = []
    for provider, model in panel:
        row = selected.get((provider, model), {})
        value = row.get("value", "")
        valid = (
            row.get("verdict") in {"correct", "incorrect"}
            and value not in {None, ""}
            and bool((row.get("sql") or "").strip())
        )
        parsed_value = None
        if valid:
            try:
                parsed_value = int(value)
            except (TypeError, ValueError):
                pass

        proposals.append(SimpleNamespace(
            provider=provider,
            model_requested=model,
            value=parsed_value,
            verdict="executed" if parsed_value is not None else "error"
        ))
    return proposals


def evaluate(vote, proposals, reference=None):
    result = vote(proposals, 2)
    required = {"consensus", "value", "votes", "models"}
    if not isinstance(result, dict) or not required <= result.keys():
        raise ValueError("Return consensus, value, votes and models as specified in TD2.")
    # Correctness is evaluated AFTER the decision, never used to choose a vote.
    return {"decision": result, "reference": reference,
            "matches_reference": (result["value"] == reference)
            if reference is not None and result["consensus"] else None}


def compare_panels(rows, nature):
    """Compare the fixed 2-of-3 and 3-of-5 quorums on the same twenty cases."""
    questions_path = Path(__file__).with_name("questions-td1.json")
    questions = json.loads(questions_path.read_text(encoding="utf-8"))["questions"]
    question_ids = {q["id"] for q in questions}
    references = {}
    for row in rows:
        if row["nature"] != nature or row["case_id"] not in question_ids:
            continue
        reference = (row.get("reference") or "").strip()
        if reference:
            value = int(reference)
            existing = references.setdefault(row["case_id"], value)
            if existing != value:
                raise ValueError(f"Conflicting references for {row['case_id']}.")

    missing = [q["id"] for q in questions if q["id"] not in references]
    if missing:
        raise ValueError(f"Missing reference values for: {', '.join(missing)}")

    vote = load_vote()
    panels = [
        ("2of3", PANEL, 2),
        ("3of5", PANEL_FIVE, 3),
    ]
    output = []
    summary = {
        name: {"questions": len(questions), "consensus": 0, "abstentions": 0, "correct": 0}
        for name, _, _ in panels
    }

    for question in questions:
        row = {"case_id": question["id"], "question": question["question"],
               "reference": references[question["id"]]}
        for name, panel, k in panels:
            decision = vote(proposals_for(rows, question["id"], nature, panel), k)
            correct = decision["consensus"] and decision["value"] == row["reference"]
            row.update({
                f"{name}_consensus": decision["consensus"],
                f"{name}_value": decision["value"],
                f"{name}_votes": decision["votes"],
                f"{name}_correct": correct if decision["consensus"] else "",
            })
            summary[name]["consensus"] += int(decision["consensus"])
            summary[name]["abstentions"] += int(not decision["consensus"])
            summary[name]["correct"] += int(bool(correct))
        output.append(row)

    for name in summary:
        metrics = summary[name]
        metrics["accuracy"] = metrics["correct"] / metrics["questions"]
        metrics["accuracy_given_consensus"] = (
            metrics["correct"] / metrics["consensus"] if metrics["consensus"] else None
        )
        metrics["abstention_rate"] = metrics["abstentions"] / metrics["questions"]
    summary["delta_3of5_minus_2of3"] = {
        "accuracy": summary["3of5"]["accuracy"] - summary["2of3"]["accuracy"],
        "accuracy_given_consensus": (
            summary["3of5"]["accuracy_given_consensus"] - summary["2of3"]["accuracy_given_consensus"]
            if summary["3of5"]["accuracy_given_consensus"] is not None
            and summary["2of3"]["accuracy_given_consensus"] is not None else None
        ),
        "abstention_rate": summary["3of5"]["abstention_rate"] - summary["2of3"]["abstention_rate"],
    }
    return output, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces", type=Path)
    parser.add_argument("--case", default="C01")
    parser.add_argument("--nature", choices=["real", "replay", "simulation"], default="real")
    parser.add_argument("--compare", action="store_true",
                        help="compare 2-of-3 and 3-of-5 on all twenty questions; requires references")
    parser.add_argument("--out", type=Path, help="comparison CSV path (default: vote-comparison.csv beside traces)")
    args = parser.parse_args()
    vote = load_vote()
    try:
        if args.traces:
            with args.traces.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            if args.compare:
                table, summary = compare_panels(rows, args.nature)
                out_path = args.out or args.traces.with_name("vote-comparison.csv")
                with out_path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=table[0].keys())
                    writer.writeheader()
                    writer.writerows(table)
                print(json.dumps({"comparison_csv": str(out_path), "summary": summary}))
                return 0
            relevant = [r for r in rows if r["case_id"] == args.case and r["nature"] == args.nature]
            if not relevant:
                raise ValueError("No rows for this case and nature.")
            refs = {int(r["reference"]) for r in relevant if r.get("reference") not in {None, ""}}
            if len(refs) > 1:
                raise ValueError("Conflicting references: check the experiment before voting.")
            result = evaluate(vote, proposals_for(rows, args.case, args.nature), next(iter(refs), None))
            print(json.dumps({"case": args.case, "nature": args.nature, "n": 3, "k": 2, **result}))
        else:
            if args.compare:
                raise ValueError("--compare requires --traces.")
            # Synthetic values in cents. These are not results on the shop data.
            for name, values, reference in [
                ("agreement", [100, 100, 120], 100),
                ("disagreement", [100, 110, 120], 100),
                ("unavailable", [100, None, None], 100),
                ("wrong consensus", [0, 0, 100], 100),
            ]:
                proposals = [SimpleNamespace(provider=p, model_requested=m, value=v,
                                             verdict="executed" if v is not None else "error")
                             for (p, m), v in zip(PANEL, values)]
                print(json.dumps({"example": name, "nature": "simulation", "n": 3, "k": 2,
                                  **evaluate(vote, proposals, reference)}))
    except (NotImplementedError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
