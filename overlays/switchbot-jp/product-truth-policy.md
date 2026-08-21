# Product Truth Policy

## Authority

Product Truth is an upstream input to Listing Planning. Listing Planning,
Production, and Hardening may reference it but must not overwrite it.

Use the existing Product Knowledge Hub as the normalized product-fact gate and
Feishu as discovery/evidence. Use the latest applicable, authoritative canonical
record or explicitly approved project decision. Newer does not automatically
mean more authoritative. Retain source ID, version/revision, scope, market,
validity dates, retrieval time, review status, and conflicts.

## Required packet

Every project must create a Product Truth Packet containing:

- Product;
- SKU / Offer;
- Specifications;
- Approved Claims;
- Unapproved Claims;
- Compatibility;
- Installation;
- Target User;
- User Scenario;
- Pricing;
- Bundle;
- Available Assets;
- Forbidden Claims;
- Unknown / TBD;
- Sources.

## State rules

Use `CONFIRMED`, `CONDITIONAL`, `CONFLICT`, `MISSING`, `PROHIBITED`, and
`UNKNOWN` for fact-bearing items. A missing or conflicted value remains visible;
do not average, infer, translate into certainty, or fill it for completeness.

The packet must be validated and frozen with a SHA-256 lock before Planning.
Any update creates a new packet revision and lock. Downstream artifacts record
the packet ID and hash they used.

## Gate

`PRODUCT_TRUTH_GATE` is `PASS` only when the packet is structurally valid and
all claims intended for consumer use have an explicit approved state. It is
`BLOCKED` when required product identity, offer scope, or source traceability is
missing. Other unknowns may remain open only when their downstream dependencies
are explicitly listed.
