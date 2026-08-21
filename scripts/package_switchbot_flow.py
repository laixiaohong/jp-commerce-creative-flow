#!/usr/bin/env python3
"""Package upstream five Skills plus the SwitchBot JP wrapper and Overlay."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / ".agents" / "skills"
OVERLAY = REPO / "overlays" / "switchbot-jp"
DIST = REPO / "dist"
OUTPUT = DIST / "jp-commerce-creative-flow-codex-bundle.zip"
SKILL_NAMES = [
    "jp-commerce-creative-flow",
    "japan-listing-demo",
    "listing-planning",
    "listing-production",
    "listing-hardening",
    "listing-evidence-auditor",
]


def add_tree(archive: ZipFile, root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            archive.write(path, path.relative_to(REPO))


def main() -> None:
    for name in SKILL_NAMES:
        skill = SKILLS / name / "SKILL.md"
        if not skill.is_file():
            raise SystemExit(f"FAIL: missing {skill.relative_to(REPO)}")
    if not (OVERLAY / "manifest.json").is_file():
        raise SystemExit("FAIL: missing SwitchBot JP Overlay manifest")

    DIST.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for name in SKILL_NAMES:
            add_tree(archive, SKILLS / name)
        add_tree(archive, OVERLAY)
        add_tree(archive, REPO / "docs" / "switchbot-jp")

    with ZipFile(OUTPUT) as archive:
        members = set(archive.namelist())
    required = {
        ".agents/skills/jp-commerce-creative-flow/SKILL.md",
        ".agents/skills/japan-listing-demo/SKILL.md",
        ".agents/skills/listing-planning/SKILL.md",
        ".agents/skills/listing-production/SKILL.md",
        ".agents/skills/listing-hardening/SKILL.md",
        ".agents/skills/listing-evidence-auditor/SKILL.md",
        "overlays/switchbot-jp/manifest.json",
        "overlays/switchbot-jp/schemas/product-truth-packet.schema.json",
    }
    missing = sorted(required - members)
    if missing:
        raise SystemExit("FAIL: package missing " + ", ".join(missing))
    print(f"PASS: SwitchBot bundle contains {len(members)} files across six Skills plus Overlay")
    print(OUTPUT)


if __name__ == "__main__":
    main()
