"""Freeze the human-only baseline (docs/specs/09-research/evaluation-protocol.md Stage B).

Writes a timestamped snapshot of the baseline metrics to docs/baselines/ as
machine-readable JSON plus a Markdown summary for the written report. Phase 3
compares hybrid AI results against the JSON file; nothing recomputes the
baseline later, which is the point of freezing it.

    cd backend && .venv/Scripts/python.exe ../scripts/freeze_baseline.py
    cd backend && .venv/Scripts/python.exe ../scripts/freeze_baseline.py --from 2026-10-01 --to 2026-10-31 --label uat-round-1

Refuses to write while AI or WhatsApp are enabled: a baseline collected with
assistance turned on is not a human-only baseline, and silently mislabelling one
would corrupt every later comparison.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services.metrics_service import compute_baseline_metrics  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "docs" / "baselines"


def parse_moment(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise SystemExit(f"Could not read '{value}' as a date. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.")


def format_value(entry):
    if entry["value"] is None:
        return "not measured"
    if entry["unit"] == "ratio":
        return f"{entry['value'] * 100:.1f}%"
    if entry["unit"] == "seconds":
        seconds = entry["value"]
        if seconds < 90:
            return f"{seconds:.0f}s"
        if seconds < 5400:
            return f"{seconds / 60:.1f} min"
        return f"{seconds / 3600:.1f} h"
    return f"{entry['value']:.0f}"


def render_markdown(payload, label):
    lines = [
        f"# Human-only baseline — {label}",
        "",
        f"Generated {payload['generated_at']} from the {payload['phase']} build "
        f"(AI enabled: {payload['ai_enabled']}, WhatsApp enabled: {payload['whatsapp_enabled']}).",
        "",
        f"Window: {payload['window_start'] or 'start of records'} to {payload['window_end'] or 'now'}.",
        "",
        "## Volumes",
        "",
        "| Activity | Count |",
        "| --- | ---: |",
    ]
    for key, count in payload["volumes"].items():
        lines.append(f"| {key.replace('_', ' ').capitalize()} | {count} |")

    lines += ["", "## Measured", "", "| Metric | Value | Sample | Definition |", "| --- | ---: | ---: | --- |"]
    for entry in payload["metrics"]:
        lines.append(
            f"| {entry['label']} | {format_value(entry)} | {entry['sample_size']} | {entry['definition']} |"
        )

    lines += ["", "## Not measured", "", "| Metric | Why | How to collect |", "| --- | --- | --- |"]
    for entry in payload["unavailable_metrics"]:
        lines.append(f"| {entry['label']} | {entry['reason']} | {entry['how_to_collect']} |")

    if payload["moderator_workload"]:
        lines += ["", "## Moderator workload", "", "| Moderator | Decisions | Median review time |", "| --- | ---: | ---: |"]
        for entry in payload["moderator_workload"]:
            median = entry["median_review_seconds"]
            rendered = "not measured" if median is None else f"{median / 60:.1f} min"
            lines.append(f"| {entry['name_or_alias']} | {entry['decisions']} | {rendered} |")

    lines += ["", "## Interpretation", "", payload["interpretation_note"], ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Freeze the human-only baseline metrics.")
    parser.add_argument("--from", dest="start", help="Inclusive window start (YYYY-MM-DD).")
    parser.add_argument("--to", dest="end", help="Inclusive window end (YYYY-MM-DD).")
    parser.add_argument("--label", default=None, help="Short name for this baseline, e.g. uat-round-1.")
    parser.add_argument(
        "--allow-assisted",
        action="store_true",
        help="Write the snapshot even though AI or WhatsApp is enabled. The result is NOT a human-only baseline.",
    )
    args = parser.parse_args()

    if (settings.AI_ENABLED or settings.WHATSAPP_ENABLED) and not args.allow_assisted:
        raise SystemExit(
            "Refusing to freeze a human-only baseline while AI_ENABLED or WHATSAPP_ENABLED is true.\n"
            "Turn them off and re-run, or pass --allow-assisted if you deliberately want an assisted snapshot."
        )

    start = parse_moment(args.start)
    end = parse_moment(args.end)
    if start and end and start > end:
        raise SystemExit("The start of the window must not be after its end.")

    label = args.label or datetime.utcnow().strftime("%Y-%m-%d")
    db = SessionLocal()
    try:
        payload = json.loads(compute_baseline_metrics(db, start=start, end=end).model_dump_json())
    finally:
        db.close()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / f"baseline-{label}.json"
    md_path = OUTPUT_DIR / f"baseline-{label}.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload, label), encoding="utf-8")

    measured = sum(1 for m in payload["metrics"] if m["value"] is not None)
    print(f"Baseline '{label}' frozen from {payload['volumes']['reports_submitted']} reports.")
    print(f"  {measured} of {len(payload['metrics'])} metrics measured; "
          f"{len(payload['unavailable_metrics'])} need offline collection.")
    print(f"  {json_path.relative_to(REPO_ROOT)}")
    print(f"  {md_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
