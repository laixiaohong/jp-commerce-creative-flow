# Asset Policy

## Source classes

- `OFFICIAL_APPROVED`: approved official product/brand/UI/packaging asset;
- `OFFICIAL_PENDING`: official source whose final-use approval is pending;
- `DERIVATIVE_AUTHORIZED`: derivative with parent, transform, scope, and human
  authorization recorded;
- `REFERENCE_ONLY`: mood, benchmark, competitor, or structural reference;
- `AI_CONCEPT_ONLY`: concept material that cannot prove product identity;
- `UNKNOWN`: insufficient provenance.

Only assets eligible under the upstream Evidence Auditor and Hardening contracts
may enter final Demo assembly.

## Exact-file rule

Filename and Asset ID are not evidence. Final approval binds to exact SHA-256,
visual role, and slot/page/offer scope. Any byte, role, scope, crop, resize,
recomposition, text, or background change requires derivative tracking and may
require new approval.

## Public boundary

Do not commit real product assets, Feishu downloads, internal approval records,
or unreleased visuals to this public repository. Golden Fixtures contain only
synthetic metadata and expectations.

## Gate

`ASSET_GATE` cannot pass through self-report. Use the upstream independent
Evidence Auditor and retain `HUMAN_REVIEW_REQUIRED` where semantic review is not
independent.
