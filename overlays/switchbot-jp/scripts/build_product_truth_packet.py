#!/usr/bin/env python3
"""Build and freeze a Product Truth Packet from a reviewed normalized intake."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def normalize_claims(packet: dict[str, Any]) -> None:
    approved: list[dict[str, Any]] = []
    demoted: list[dict[str, Any]] = list(packet.get("unapproved_claims", []))
    for claim in packet.get("approved_claims", []):
        approval = claim.get("approval") or {}
        valid = (
            approval.get("status") == "APPROVED"
            and bool(approval.get("approved_by"))
            and bool(approval.get("approved_at"))
            and bool(claim.get("source_refs"))
            and claim.get("locale") == "ja-JP"
            and bool(claim.get("scope"))
        )
        if valid:
            approved.append(claim)
        else:
            demoted.append(
                {
                    "id": claim.get("id", "CLAIM-UNIDENTIFIED"),
                    "statement": claim.get("statement", "Missing claim statement"),
                    "status": "PENDING",
                    "reason": "Approval record incomplete; automatically kept out of Approved Claims",
                    "source_refs": claim.get("source_refs", []),
                }
            )
    packet["approved_claims"] = approved
    packet["unapproved_claims"] = demoted


def build(reviewed_intake: dict[str, Any]) -> dict[str, Any]:
    packet = dict(reviewed_intake)
    normalize_claims(packet)
    return packet


def freeze(packet: dict[str, Any]) -> dict[str, str]:
    digest = hashlib.sha256(canonical_bytes(packet)).hexdigest()
    return {
        "schema_version": "1.0",
        "packet_id": str(packet.get("packet_id", "")),
        "packet_sha256": digest,
        "rule": "Downstream artifacts may reference but must not overwrite this packet",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Human-reviewed normalized intake JSON")
    parser.add_argument("output", type=Path)
    parser.add_argument("--lock", type=Path, required=True)
    args = parser.parse_args()
    reviewed = json.loads(args.input.read_text(encoding="utf-8"))
    packet = build(reviewed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lock = freeze(packet)
    args.lock.parent.mkdir(parents=True, exist_ok=True)
    args.lock.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: Product Truth Packet frozen at {lock['packet_sha256']}")


if __name__ == "__main__":
    main()
