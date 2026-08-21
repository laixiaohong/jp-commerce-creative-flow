#!/usr/bin/env python3
"""Create a conservative compatibility report for an upstream update."""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROTECTED_PREFIXES = (
    ".agents/skills/japan-listing-demo/",
    ".agents/skills/listing-planning/",
    ".agents/skills/listing-production/",
    ".agents/skills/listing-hardening/",
    ".agents/skills/listing-evidence-auditor/",
    "scripts/package_codex_bundle.py",
    ".github/workflows/validate-japan-listing-demo.yml",
)
HIGH_RISK_MARKERS = (
    "SKILL.md",
    "channel-policy-limits.json",
    "validate_",
    "selftest_",
    "reconcile_evidence.py",
    "fingerprint_assets.py",
)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def changed_files(base_ref: str, head_ref: str) -> list[tuple[str, str]]:
    output = git("diff", "--name-status", f"{base_ref}..{head_ref}")
    rows: list[tuple[str, str]] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0], parts[-1]))
    return rows


def classify(rows: list[tuple[str, str]]) -> tuple[str, list[str], list[str]]:
    protected = [path for _, path in rows if path.startswith(PROTECTED_PREFIXES)]
    high_risk = [path for path in protected if any(marker in path for marker in HIGH_RISK_MARKERS)]
    if not rows:
        return "NO_UPDATE", protected, high_risk
    if high_risk:
        return "HUMAN_REVIEW_REQUIRED", protected, high_risk
    if protected:
        return "REGRESSION_REVIEW_REQUIRED", protected, high_risk
    return "LOW_CORE_RISK_REVIEW_REQUIRED", protected, high_risk


def render(base_ref: str, head_ref: str, test_status: str) -> str:
    rows = changed_files(base_ref, head_ref)
    status, protected, high_risk = classify(rows)
    base_sha = git("rev-parse", base_ref)
    head_sha = git("rev-parse", head_ref)
    lines = [
        "# Upstream Upgrade Report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Base: `{base_ref}` / `{base_sha}`",
        f"- Upstream: `{head_ref}` / `{head_sha}`",
        f"- Compatibility status: **{status}**",
        f"- Regression tests: **{test_status}**",
        "- Merge policy: Draft PR + human review; never auto-merge",
        "",
        "## Summary",
        "",
        f"- Changed files: {len(rows)}",
        f"- Upstream-core files changed: {len(protected)}",
        f"- High-risk contract/validator files changed: {len(high_risk)}",
        "",
        "## Changed files",
        "",
    ]
    if rows:
        lines.extend(f"- `{change}` `{path}`" for change, path in rows)
    else:
        lines.append("- None")
    lines.extend(["", "## Required human review", ""])
    lines.extend(
        [
            "- Confirm Product Truth cannot be overwritten downstream.",
            "- Confirm Claim approval remains human-owned.",
            "- Confirm Gallery/A+ role separation and module ceilings.",
            "- Confirm Asset, Human Review, Evidence Auditor, and Hardening gates.",
            "- Inspect all high-risk files listed below.",
            "",
            "## High-risk files",
            "",
        ]
    )
    lines.extend((f"- `{path}`" for path in high_risk),)
    if not high_risk:
        lines.append("- None detected; human review is still required.")
    lines.extend(["", "## Decision", "", "Do not merge until CI and human review are complete.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--test-status", default="NOT_RUN")
    args = parser.parse_args()
    report = render(args.base_ref, args.head_ref, args.test_status)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
