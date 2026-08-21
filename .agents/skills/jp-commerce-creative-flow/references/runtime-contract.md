# Runtime contract

## Ownership

| Layer | Owns | Must not own |
|---|---|---|
| Source Layer | Read-only Feishu/Product Knowledge intake and source snapshots | Claim approval |
| Product Truth Packet | Normalized fact, claim, offer, asset and unknown state | Creative strategy or asset production |
| SwitchBot JP Overlay | Business rules and human review requirements | Upstream stage implementation |
| `japan-listing-demo` | Router, checkpoints, context firewall and stage routing | Private business facts |
| `listing-planning` | Stage 0–7 planning and production handoff | Final visual production or evidence certification |
| `listing-production` | Stage 7.5–8 one-job artifact production | Product Truth mutation or final hardening |
| `listing-hardening` | Stage 8.5–10 final-file and delivery QA | Strategy reinterpretation |
| `listing-evidence-auditor` | Exact-file, provenance, approval and semantic evidence reconciliation | Creative repair or self-approval |

## Required project files

Store runtime data outside this public repository, for example:

```text
<project>/source-snapshots/
<project>/product-truth/product-truth-packet.json
<project>/product-truth/product-truth-packet.lock.json
<project>/planning/
<project>/production/
<project>/hardening/
```

## Gate order

1. `SOURCE_INTAKE_GATE`
2. `PRODUCT_TRUTH_GATE`
3. upstream Planning checkpoints
4. `CLAIM_HUMAN_REVIEW_GATE`
5. `VISUAL_DIRECTION_HUMAN_REVIEW_GATE`
6. upstream Production Freeze gates
7. upstream Evidence Reconciliation and Hardening gates
8. `FINAL_VISUAL_HUMAN_REVIEW_GATE`

No downstream status may rewrite an earlier truth or approval status.

## Failure semantics

- `PASS`: all required evidence for this gate exists.
- `PARTIAL`: progress is allowed only where the upstream contract explicitly permits it.
- `BLOCKED`: do not advance; report the exact missing field/source/approval.
- `HUMAN_REVIEW_REQUIRED`: deterministic checks may pass, but human judgment remains required.

`继续` or another Transition Command advances only where the upstream Router permits it. It never changes `BLOCKED`, `UNAPPROVED`, `UNKNOWN`, or `HUMAN_REVIEW_REQUIRED` into approval.
