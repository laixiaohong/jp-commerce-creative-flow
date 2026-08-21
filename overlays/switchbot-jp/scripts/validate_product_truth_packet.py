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
SOURCE_STATUSES = {"VERIFIED_READ", "PARTIAL", "STALE", "CONFLICT", "BLOCKED"}
UNAPPROVED_STATUSES = {"PENDING", "CONFLICT", "PROHIBITED", "UNKNOWN"}
ASSET_CLASSES = {"OFFICIAL_APPROVED", "OFFICIAL_PENDING", "DERIVATIVE_AUTHORIZED", "REFERENCE_ONLY", "AI_CONCEPT_ONLY", "UNKNOWN"}
ASSET_STATUSES = {"AVAILABLE", "PENDING", "MISSING", "BLOCKED"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def check_object(
    value: Any,
    *,
    label: str,
    required: set[str],
    allowed: set[str],
    errors: list[str],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{label} missing keys: {', '.join(missing)}")
    extra = sorted(set(value) - allowed)
    if extra:
        errors.append(f"{label} has unknown keys: {', '.join(extra)}")
    return value


def check_refs(refs: Any, *, label: str, source_ids: set[str], errors: list[str], required: bool = False) -> None:
    if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref for ref in refs):
        errors.append(f"{label}.source_refs must be a list of non-empty strings")
        return
    if required and not refs:
        errors.append(f"{label}.source_refs is required")
    if len(refs) != len(set(refs)):
        errors.append(f"{label}.source_refs contains duplicates")
    for ref in refs:
        if ref not in source_ids:
            errors.append(f"{label} references unknown source {ref}")


def validate(packet: dict[str, Any], lock: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be an object"]
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
    for key in ("packet_id", "generated_at"):
        if not isinstance(packet.get(key), str) or not packet.get(key):
            errors.append(f"{key} must be a non-empty string")
    if not isinstance(packet.get("revision"), int) or packet.get("revision", 0) < 1:
        errors.append("revision must be a positive integer")
    product = check_object(
        packet.get("product"),
        label="product",
        required={"name", "status", "source_refs"},
        allowed={"name", "official_name_ja", "category", "status", "source_refs"},
        errors=errors,
    )
    if product is not None:
        if not isinstance(product.get("name"), str) or not product.get("name"):
            errors.append("product.name is required")
        if product.get("status") not in FACT_STATUSES:
            errors.append("product.status is invalid")
    for key in LIST_KEYS:
        if key in packet and not isinstance(packet[key], list):
            errors.append(f"{key} must be a list")

    source_ids: set[str] = set()
    for source in packet.get("sources", []):
        source = check_object(
            source,
            label="source",
            required={"id", "source_type", "title", "original_url", "token", "updated_at", "retrieved_at", "content_sha256", "status"},
            allowed={"id", "source_type", "title", "original_url", "token", "updated_at", "retrieved_at", "content_sha256", "status"},
            errors=errors,
        )
        if source is None:
            continue
        sid = source.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append("every source requires id")
            continue
        if sid in source_ids:
            errors.append(f"duplicate source id: {sid}")
        source_ids.add(sid)
        if source.get("source_type") not in SOURCE_TYPES:
            errors.append(f"invalid source_type for {sid}")
        if source.get("status") not in SOURCE_STATUSES:
            errors.append(f"invalid source status for {sid}")
        if not isinstance(source.get("retrieved_at"), str) or not source.get("retrieved_at"):
            errors.append(f"retrieved_at is required for {sid}")
        digest = source.get("content_sha256", "")
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            errors.append(f"invalid content_sha256 for {sid}")

    for claim in packet.get("approved_claims", []):
        claim = check_object(
            claim,
            label="approved claim",
            required={"id", "statement", "locale", "scope", "conditions", "source_refs", "approval"},
            allowed={"id", "statement", "locale", "scope", "conditions", "source_refs", "approval"},
            errors=errors,
        )
        if claim is None:
            continue
        cid = claim.get("id", "<unknown>")
        if not isinstance(cid, str) or not cid or not isinstance(claim.get("statement"), str) or not claim.get("statement"):
            errors.append("approved claim id and statement are required")
        if not isinstance(claim.get("conditions"), list) or any(not isinstance(item, str) for item in claim.get("conditions", [])):
            errors.append(f"approved claim {cid} conditions must be a list of strings")
        approval = check_object(
            claim.get("approval"),
            label=f"approved claim {cid} approval",
            required={"status", "approved_by", "approved_at"},
            allowed={"status", "approved_by", "approved_at"},
            errors=errors,
        ) or {}
        if approval.get("status") != "APPROVED" or not approval.get("approved_by") or not approval.get("approved_at"):
            errors.append(f"approved claim {cid} lacks complete human approval")
        if claim.get("locale") != "ja-JP" or not claim.get("scope"):
            errors.append(f"approved claim {cid} lacks locale/scope/source")
        check_refs(claim.get("source_refs"), label=f"approved claim {cid}", source_ids=source_ids, errors=errors, required=True)

    if not packet.get("sources"):
        errors.append("at least one source is required")

    if product is not None:
        check_refs(product.get("source_refs"), label="product", source_ids=source_ids, errors=errors, required=True)

    for section in FACT_LISTS:
        for item in packet.get(section, []):
            item = check_object(
                item,
                label=f"{section} item",
                required={"id", "label", "value", "status", "source_refs"},
                allowed={"id", "label", "value", "status", "scope", "conditions", "source_refs"},
                errors=errors,
            )
            if item is None:
                continue
            iid = item.get("id", "<unknown>")
            if not isinstance(iid, str) or not iid or not isinstance(item.get("label"), str) or not item.get("label"):
                errors.append(f"{section} item id and label are required")
            if item.get("status") not in FACT_STATUSES:
                errors.append(f"{section} item {iid} has invalid status")
            if "conditions" in item and (not isinstance(item["conditions"], list) or any(not isinstance(value, str) for value in item["conditions"])):
                errors.append(f"{section} item {iid} conditions must be a list of strings")
            has_value = item.get("value") not in (None, "")
            check_refs(item.get("source_refs"), label=f"{section} item {iid}", source_ids=source_ids, errors=errors, required=has_value)

    for section in EVIDENCE_LISTS:
        for item in packet.get(section, []):
            item = check_object(
                item,
                label=f"{section} item",
                required={"id", "statement", "status", "source_refs"},
                allowed={"id", "statement", "status", "source_refs"},
                errors=errors,
            )
            if item is None:
                continue
            iid = item.get("id", "<unknown>")
            if not isinstance(iid, str) or not iid or not isinstance(item.get("statement"), str) or not item.get("statement"):
                errors.append(f"{section} item id and statement are required")
            if item.get("status") not in FACT_STATUSES:
                errors.append(f"{section} item {iid} has invalid status")
            check_refs(item.get("source_refs"), label=f"{section} item {iid}", source_ids=source_ids, errors=errors, required=True)

    for claim in packet.get("unapproved_claims", []):
        claim = check_object(
            claim,
            label="unapproved claim",
            required={"id", "statement", "status", "reason", "source_refs"},
            allowed={"id", "statement", "status", "reason", "source_refs"},
            errors=errors,
        )
        if claim is None:
            continue
        cid = claim.get("id", "<unknown>")
        if not isinstance(cid, str) or not cid or not isinstance(claim.get("statement"), str) or not claim.get("statement") or not isinstance(claim.get("reason"), str) or not claim.get("reason"):
            errors.append("unapproved claim id, statement, and reason are required")
        if claim.get("status") not in UNAPPROVED_STATUSES:
            errors.append(f"unapproved claim {cid} has invalid status")
        check_refs(claim.get("source_refs"), label=f"unapproved claim {cid}", source_ids=source_ids, errors=errors)

    for asset in packet.get("available_assets", []):
        asset = check_object(
            asset,
            label="asset",
            required={"id", "class", "path_or_ref", "status", "source_refs"},
            allowed={"id", "class", "path_or_ref", "status", "source_refs"},
            errors=errors,
        )
        if asset is None:
            continue
        aid = asset.get("id", "<unknown>")
        if not isinstance(aid, str) or not aid:
            errors.append("asset id is required")
        if asset.get("class") not in ASSET_CLASSES:
            errors.append(f"asset {aid} has invalid class")
        if asset.get("status") not in ASSET_STATUSES:
            errors.append(f"asset {aid} has invalid status")
        check_refs(asset.get("source_refs"), label=f"asset {aid}", source_ids=source_ids, errors=errors, required=asset.get("path_or_ref") not in (None, ""))

    for item in packet.get("unknown_tbd", []):
        item = check_object(
            item,
            label="unknown_tbd item",
            required={"id", "question", "owner", "deadline", "blocks"},
            allowed={"id", "question", "owner", "deadline", "blocks"},
            errors=errors,
        )
        if item is None:
            continue
        if not isinstance(item.get("id"), str) or not item.get("id") or not isinstance(item.get("question"), str) or not item.get("question"):
            errors.append("unknown_tbd id and question are required")
        if not isinstance(item.get("blocks"), list) or any(not isinstance(value, str) or not value for value in item.get("blocks", [])):
            errors.append(f"unknown_tbd {item.get('id', '<unknown>')} blocks must be a list of non-empty strings")

    if lock is not None:
        lock_object = check_object(
            lock,
            label="lock",
            required={"schema_version", "packet_id", "packet_sha256", "rule"},
            allowed={"schema_version", "packet_id", "packet_sha256", "rule"},
            errors=errors,
        )
        if lock_object is None:
            return errors
        actual = hashlib.sha256(canonical_bytes(packet)).hexdigest()
        if lock_object.get("schema_version") != "1.0":
            errors.append("lock schema_version must be 1.0")
        if lock_object.get("packet_id") != packet.get("packet_id"):
            errors.append("lock packet_id mismatch")
        if lock_object.get("packet_sha256") != actual:
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
