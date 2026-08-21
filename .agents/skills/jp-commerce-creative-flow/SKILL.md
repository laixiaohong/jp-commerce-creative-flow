---
name: jp-commerce-creative-flow
description: Use when running a SwitchBot Japan Amazon/Japan-commerce creative project from Feishu or Product Knowledge intake through Product Truth, planning, human review, production, hardening, and evidence audit.
---

# JP Commerce Creative Flow

## Purpose

One user entry: `$jp-commerce-creative-flow`.

This Skill is a thin SwitchBot JP control layer over the upstream five-Skill
`$japan-listing-demo` runtime. It adds source governance and business policy; it
does not copy or replace Planning, Production, Hardening, or Evidence Auditor.

Read `references/runtime-contract.md`, then load
`../../../overlays/switchbot-jp/manifest.json` and only the policy files needed
for the current stage.

## Fixed route

```text
Source Intake
→ Product Truth Packet
→ SwitchBot JP Overlay
→ $japan-listing-demo Planning
→ Human Review Gate
→ Production
→ Hardening + Evidence Auditor
```

The user must not be asked to invoke internal Skills manually.

## Source Intake

For a supplied Feishu URL, prefer the read-only MCP tool
`get_feishu_resource`. Its formal scope is Docx, Sheet, and Bitable. If the
tool is unavailable or the resource cannot be read, return `BLOCKED`; do not
pretend the source was read. Normalize each successful result according to
`feishu-source-policy.md` before using it.

Invoke/read the existing `$product-knowledge` Skill as the product-fact gate.
Resolve the exact product/variant/bundle in its runtime index, then verify the
required canonical records described in `product-knowledge-policy.md`. Feishu
raw content and Product Knowledge extracts are source inputs, not
consumer-ready claims.

## Product Truth Gate

Generate and validate a `Product Truth Packet` before Planning. Keep Product,
SKU/Offer, Specifications, Approved/Unapproved Claims, Compatibility,
Installation, Target User, User Scenario, Pricing, Bundle, Available Assets,
Forbidden Claims, Unknown/TBD, and Sources separate.

Freeze the validated packet with its SHA-256 lock. Downstream Skills may derive
state from it but must not overwrite it. Missing, stale, conflicted, or
unapproved facts stay visible.

Do not enter Planning when the packet validator returns `BLOCKED`.

## Upstream handoff

After the Product Truth Gate, invoke the existing `$japan-listing-demo` Router
and preserve all of its stage ownership, Context Firewall, Retry Budget,
Major Stage Checkpoints, executable gates, and independent/human semantic
review limitations.

At every major checkpoint, use:

```text
Done:
Open:
Next:
```

No Claim, production direction, or final visual becomes approved without the
explicit human review required by the Overlay.

## Public repository boundary

This repository is public. Commit only policies, schemas, scripts, synthetic
fixtures, and empty templates. Store real Feishu snapshots, Product Truth
Packets, prices, unreleased facts, approvals, and product assets outside the
repository in the project workspace.
