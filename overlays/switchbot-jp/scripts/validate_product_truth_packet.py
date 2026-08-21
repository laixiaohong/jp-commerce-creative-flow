#!/usr/bin/env python3
"""Dependency-free structural and truth-boundary validator."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_KEYS = {
    "schema_version", "packet_id", "revision", "generated_at", "market", "product",
    "sku_offers", "specifications", "approved_claims", "unapproved_claims",
    "compatibility", "installation", "target_users", "user_scenarios", "pricing",
    "bundles", "available_assets", "forbidden_claims", "unknown_tbd", "sources",
}
LIST_KEYS = REQUIRED_KEYS - {"schema_version", "packet_id", "revision", "generated_at", "market", "product"}
FACT_STATUSES = {"CONFIRMED", "CONDITIONAL", "CONFLICT", "MISSING", "PROHIBITED", "UNKNOWN"}
SOURCE_TYPES = {"feishu_docx", "feishu_sheet", "feishu_bitable", "product_knowledge", "official_file", "human_decision"}
FACT_LISTS = {"sku_offers", "specifications", "compatibility", "installation", "pricing", "bundles"}
EVIDENCE_LISTS = {"target_users", "user_scenarios", "forbidden_claims"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def validate(packet: dict[str, Any], lock: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_KEYS - set(packet))
    if missing:
        errors.append("missing keys: " + ", ".join(missing))
    extra = sorted(set(packet) - REQUIRED_KEYS)
    if extra:
        errors.append("unknown top-level keys: " + ", ".join(extra))
    if packet.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if packet.get("market") != "JP":
        errors.append("market must be JP")
    if not isinstance(packet.get("revision"), int) or packet.get("revision", 0) < 1:
        errors.append("revision must be a positive integer")
    product = packet.get("product")
    if not isinstance(product, dict) or not product.get("name"):
        errors.append("product.name is required")
    elif product.get("status") not in FACT_STATUSES:
        errors.append("product.status is invalid")
    for key in LIST_KEYS:
        if key in packet and not isinstance(packet[key], list):
            errors.append(f"{key} must be a list")

    source_ids: set[str] = set()
    for source in packet.get("sources", []):
        sid = source.get("id") if isinstance(source, dict) else None
        if not sid:
            errors.append("every source requires id")
            continue
        if sid in source_ids:
            errors.append(f"duplicate source id: {sid}")
        source_ids.add(sid)
        if source.get("source_type") not in SOURCE_TYPES:
            errors.append(f"invalid source_type for {sid}")
        digest = source.get("content_sha256", "")
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            errors.append(f"invalid content_sha256 for {sid}")

    for claim in packet.get("approved_claims", []):
        cid = claim.get("id", "<unknown>")
        approval = claim.get("approval") or {}
        if approval.get("status") != "APPROVED" or not approval.get("approved_by") or not approval.get("approved_at"):
            errors.append(f"approved claim {cid} lacks complete human approval")
        if claim.get("locale") != "ja-JP" or not claim.get("scope") or not claim.get("source_refs"):
            errors.append(f"approved claim {cid} lacks locale/scope/source")
        for ref in claim.get("source_refs", []):
            if ref not in source_ids:
                errors.append(f"approved claim {cid} references unknown source {ref}")

    if not packet.get("sources"):
        errors.append("at least one source is required")

    product_refs = product.get("source_refs", []) if isinstance(product, dict) else []
    if not product_refs:
        errors.append("product.source_refs is required")
    for ref in product_refs:
        if ref not in source_ids:
            errors.append(f"product references unknown source {ref}")

    for section in FACT_LISTS | EVIDENCE_LISTS:
        for item in packet.get(section, []):
            if not isinstance(item, dict):
                errors.append(f"{section} contains a non-object item")
                continue
            iid = item.get("id", "<unknown>")
            if item.get("status") not in FACT_STATUSES:
                errors.append(f"{section} item {iid} has invalid status")
            for ref in item.get("source_refs", []):
                if ref not in source_ids:
                    errors.append(f"{section} item {iid} references unknown source {ref}")

    for claim in packet.get("unapproved_claims", []):
        cid = claim.get("id", "<unknown>") if isinstance(claim, dict) else "<unknown>"
        if not isinstance(claim, dict) or claim.get("status") not in {"PENDING", "CONFLICT", "PROHIBITED", "UNKNOWN"}:
            errors.append(f"unapproved claim {cid} has invalid status")
            continue
        for ref in claim.get("source_refs", []):
            if ref not in source_ids:
                errors.append(f"unapproved claim {cid} references unknown source {ref}")

    for asset in packet.get("available_assets", []):
        aid = asset.get("id", "<unknown>") if isinstance(asset, dict) else "<unknown>"
        if not isinstance(asset, dict):
            errors.append("available_assets contains a non-object item")
            continue
        if asset.get("class") not in {"OFFICIAL_APPROVED", "OFFICIAL_PENDING", "DERIVATIVE_AUTHORIZED", "REFERENCE_ONLY", "AI_CONCEPT_ONLY", "UNKNOWN"}:
            errors.append(f"asset {aid} has invalid class")
        if asset.get("status") not in {"AVAILABLE", "PENDING", "MISSING", "BLOCKED"}:
            errors.append(f"asset {aid} has invalid status")
        for ref in asset.get("source_refs", []):
            if ref not in source_ids:
                errors.append(f"asset {aid} references unknown source {ref}")

    if lock is not None:
        actual = hashlib.sha256(canonical_bytes(packet)).hexdigest()
        if lock.get("packet_id") != packet.get("packet_id"):
            errors.append("lock packet_id mismatch")
        if lock.get("packet_sha256") != actual:
            errors.append("Product Truth Packet hash changed after freeze")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--lock", type=Path)
    args = parser.parse_args()
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    lock = json.loads(args.lock.read_text(encoding="utf-8")) if args.lock else None
    errors = validate(packet, lock)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}")
        raise SystemExit(1)
    print("PASS: Product Truth Packet structure, claim boundary, sources, and lock are valid")


if __name__ == "__main__":
    main()
