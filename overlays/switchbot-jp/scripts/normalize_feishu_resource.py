#!/usr/bin/env python3
"""Normalize a get_feishu_resource result into a source-grounded snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_TYPES = {"docx", "sheet", "bitable"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def normalize(payload: dict[str, Any], retrieved_at: str | None = None) -> dict[str, Any]:
    source = payload.get("source")
    resource_type = str(payload.get("resource_type", "")).lower()
    if source != "feishu":
        raise ValueError("source must be 'feishu'")
    if resource_type not in ALLOWED_TYPES:
        raise ValueError(f"unsupported resource_type: {resource_type!r}")
    for field in ("original_url", "token"):
        if not payload.get(field):
            raise ValueError(f"missing required field: {field}")
    if "content" not in payload:
        raise ValueError("missing required field: content")

    content = payload["content"]
    return {
        "source": "feishu",
        "resource_type": resource_type,
        "title": payload.get("title"),
        "original_url": payload["original_url"],
        "token": payload["token"],
        "updated_at": payload.get("updated_at"),
        "retrieved_at": retrieved_at or datetime.now(timezone.utc).isoformat(),
        "status": payload.get("status", "VERIFIED_READ"),
        "truncated": bool(payload.get("truncated", False)),
        "limits": payload.get("limits"),
        "content_sha256": hashlib.sha256(canonical_bytes(content)).hexdigest(),
        "content": content,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    snapshot = normalize(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: normalized Feishu {snapshot['resource_type']} snapshot")


if __name__ == "__main__":
    main()
