#!/usr/bin/env python3
"""Golden regression tests for the additive SwitchBot JP Overlay."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

OVERLAY = Path(__file__).resolve().parents[1]
REPO = OVERLAY.parents[1]
FIXTURES = OVERLAY / "tests" / "fixtures"
GOLDEN = {
    "s30-mini.json": {
        "gallery_storyline": ["G1_POSITIONING", "G2_PRIMARY_PROOF", "G3_USE_CASE", "G4_COMPATIBILITY", "G5_INSTALLATION", "G6_OBJECTION", "G7_OFFER"],
        "a_plus_tier": "basic",
        "a_plus_module_count": 5,
        "approved_claim_count": 0,
        "unapproved_claim_count": 1,
    },
    "lock-ultra.json": {
        "gallery_storyline": ["G1_POSITIONING", "G2_PRIMARY_PROOF", "G3_DAILY_USE", "G4_COMPATIBILITY", "G5_INSTALLATION", "G6_TRUST", "G7_OFFER"],
        "a_plus_tier": "premium",
        "a_plus_module_count": 7,
        "approved_claim_count": 1,
        "unapproved_claim_count": 0,
    },
    "promotion-bundle.json": {
        "gallery_storyline": ["G1_OFFER_IDENTITY", "G2_BUNDLE_SCOPE", "G3_PRODUCT_VALUE", "G4_USE_CASE", "G5_TERMS", "G6_OBJECTION", "G7_CTA"],
        "a_plus_tier": "basic",
        "a_plus_module_count": 5,
        "approved_claim_count": 0,
        "unapproved_claim_count": 0,
    },
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("product_truth_builder", OVERLAY / "scripts" / "build_product_truth_packet.py")
validator = load_module("product_truth_validator", OVERLAY / "scripts" / "validate_product_truth_packet.py")
normalizer = load_module("feishu_normalizer", OVERLAY / "scripts" / "normalize_feishu_resource.py")


def check_required_overlay_files() -> None:
    manifest = json.loads((OVERLAY / "manifest.json").read_text(encoding="utf-8"))
    for policy in manifest["policies"]:
        assert (OVERLAY / policy).is_file(), policy
    assert (OVERLAY / manifest["schemas"]["product_truth_packet"]).is_file()
    assert manifest["extends"] == "$japan-listing-demo"
    assert manifest["entry_skill"] == "$jp-commerce-creative-flow"


def check_feishu_normalization() -> None:
    payload = {
        "source": "feishu",
        "resource_type": "sheet",
        "original_url": "https://example.invalid/sheets/synthetic",
        "token": "synthetic-token",
        "title": "Synthetic",
        "updated_at": None,
        "content": [["header"], ["value"]],
    }
    snapshot = normalizer.normalize(payload, "2026-08-21T00:00:00Z")
    assert snapshot["resource_type"] == "sheet"
    assert len(snapshot["content_sha256"]) == 64
    assert snapshot["content"] == payload["content"]
    try:
        normalizer.normalize({**payload, "resource_type": "wiki"})
    except ValueError:
        pass
    else:
        raise AssertionError("Wiki must stay outside formal Feishu source scope")


def check_golden_fixtures() -> None:
    channel_policy = json.loads((REPO / ".agents" / "skills" / "japan-listing-demo" / "data" / "channel-policy-limits.json").read_text(encoding="utf-8"))
    limits = channel_policy["channels"]["amazon-jp"]["enhanced_content"]
    expected_fixture_names = set(GOLDEN)
    actual_fixture_names = {path.name for path in FIXTURES.glob("*.json")}
    assert actual_fixture_names == expected_fixture_names

    for path in sorted(FIXTURES.glob("*.json")):
        fixture = json.loads(path.read_text(encoding="utf-8"))
        assert fixture["fixture_notice"].startswith("SYNTHETIC")
        original = copy.deepcopy(fixture["input_packet"])
        packet = builder.build(copy.deepcopy(original))
        lock = builder.freeze(packet)
        errors = validator.validate(packet, lock)
        assert not errors, f"{path.name}: {errors}"

        expected = fixture["regression_expectations"]
        golden = GOLDEN[path.name]
        assert expected["gallery_storyline"] == golden["gallery_storyline"], "Gallery Storyline drifted"
        assert expected["a_plus_tier"] == golden["a_plus_tier"]
        assert len(expected["a_plus_modules"]) == golden["a_plus_module_count"]
        assert len(packet["approved_claims"]) == golden["approved_claim_count"]
        assert len(packet["unapproved_claims"]) == golden["unapproved_claim_count"]
        assert packet["product"] == original["product"], "Product Truth must not be rewritten"
        assert expected["gallery_storyline"][0].startswith("G1_")
        assert len(expected["gallery_storyline"]) == len(set(expected["gallery_storyline"]))
        tier = expected["a_plus_tier"]
        assert len(expected["a_plus_modules"]) <= limits[tier]["max_modules"]
        assert expected["asset_gate"] == "BLOCKED"
        assert expected["human_review_gate"] == "REQUIRED"
        assert expected["hardening"] == "BLOCKED"
        tampered = copy.deepcopy(packet)
        tampered["product"]["name"] += " tampered"
        tamper_errors = validator.validate(tampered, lock)
        assert any("hash changed" in error for error in tamper_errors), "Frozen Product Truth tampering must fail"


def check_entry_is_thin() -> None:
    skill = (REPO / ".agents" / "skills" / "jp-commerce-creative-flow" / "SKILL.md").read_text(encoding="utf-8")
    assert "$japan-listing-demo" in skill
    assert "must not overwrite" in skill
    assert "must not be asked to invoke internal Skills" in skill
    assert len(skill.splitlines()) < 130, "entry Skill should remain a thin wrapper"


def main() -> None:
    check_required_overlay_files()
    check_feishu_normalization()
    check_golden_fixtures()
    check_entry_is_thin()
    print("PASS: SwitchBot JP Overlay policies, source normalization, Product Truth lock, three Golden Fixtures, module budgets, and human/asset/hardening gates")


if __name__ == "__main__":
    main()
