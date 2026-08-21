# Architecture Audit: Upstream Core vs SwitchBot JP Overlay

Audit target: upstream `heymio/japan-listing-demo` v0.3.1 (`b664ea3` at audit time).

## Decision

Keep the upstream five-Skill architecture intact. Add a pre-Planning Source/
Product Truth layer and a thin user entry. Do not duplicate stage logic.

## Component ownership

| Component | Current input | Current output | Gate/authority | Classification | Overlay action |
|---|---|---|---|---|---|
| `japan-listing-demo` | Current stage + formal state objects | Stage route, checkpoint, compact state | Major Stage Checkpoint, Retry Budget, Context Firewall | Upstream Core | Extend through wrapper; do not edit router logic |
| `listing-planning` | Product/offer/claim baseline, consumer/market/channel evidence | Project Brief, Creative Strategy Kernel, Production Handoff, complete asset set | Product/Offer/Claim readiness, module fit/budget | Upstream Core | Supply locked Product Truth Packet and Overlay constraints before Stage 0 |
| `listing-production` | Kernel, Handoff, one Asset Packet, approved sources/benchmarks | One artifact, Asset Ledger, Production Freeze | One-job rule, creative approval distinct from evidence | Upstream Core | Supply only approved claims/assets; add SwitchBot visual policy |
| `listing-hardening` | Production Freeze, exact files, locked plan/slot contract | Delivery State, verified/fallback Demo, final QA | Exact-file, asset-set, slot, module origin, parity | Upstream Core | Require final SwitchBot human review; retain all upstream validators |
| `listing-evidence-auditor` | Real files, approval/provenance/role/scope evidence | Evidence audit and effective asset state | Independent/human semantic review | Upstream Core | No modification; Overlay cannot self-certify |
| Feishu Source Layer | Docx/Sheet/Bitable URL | Normalized source snapshot | `SOURCE_INTAKE_GATE` | Business Customization | Prefer read-only `get_feishu_resource`; preserve metadata/hash |
| Product Knowledge adapter | Canonical Product Knowledge export | Reviewed fact candidates | Source authority/freshness | Business Customization | Merge into Product Truth Packet without auto-approving claims |
| Product Truth Packet | Reviewed source snapshots + explicit decisions | Immutable fact/claim/offer/asset baseline | `PRODUCT_TRUTH_GATE` + SHA-256 lock | Business Customization | New schema, builder and validator |
| SwitchBot JP policies | Product Truth + business rules | Constraints injected by stage | Claim/strategy/visual/final human gates | Business Customization | New `overlays/switchbot-jp/` only |

## Repeated logic and decision

| Logic | Existing owner | Do not duplicate in Overlay | Overlay-specific addition |
|---|---|---|---|
| Product/Offer/Claim truth separation | Planning | Fact status and claim-readiness reasoning | Canonical packet schema, source lineage and immutable lock |
| Amazon Gallery/A+ architecture | Planning | Gallery/A+ role split, module fit, upstream module ceiling | SwitchBot shopper-decision and Japanese native-review rules |
| Visual production | Production | One-job Asset Packet, artifact-first execution | SwitchBot identity/visual direction and approved-source restriction |
| Asset evidence | Evidence Auditor | Real-file hashes, provenance, exact approval binding, semantic role | Public/private storage classification only |
| Final QA | Hardening | Asset set, slot, module origin, frontend fidelity, parity | Explicit final SwitchBot human visual review |
| Stage routing | Router | Stage numbers, Transition Command, Retry Budget | Pre-stage Source/Product Truth route only |

## Integration seam

The safe integration seam is before upstream Planning:

```text
Feishu/Product Knowledge
→ normalized snapshots
→ reviewed Product Truth Packet + lock
→ Overlay policy projection
→ existing japan-listing-demo Router
```

Downstream state records the packet ID/hash. It does not rewrite the packet.

## Files intentionally left upstream-owned

- `.agents/skills/japan-listing-demo/`
- `.agents/skills/listing-planning/`
- `.agents/skills/listing-production/`
- `.agents/skills/listing-hardening/`
- `.agents/skills/listing-evidence-auditor/`
- `scripts/package_codex_bundle.py`
- `.github/workflows/validate-japan-listing-demo.yml`

Future upstream changes to these paths trigger compatibility review and all
regression tests. Custom behavior belongs in new Overlay, wrapper, docs, tests,
and sync workflow files.

## Known limits

- `get_feishu_resource` is a runtime MCP capability, not bundled into this
  public repository. If unavailable, Source Intake is `BLOCKED`.
- Product Knowledge remains the governed external source; this repository ships
  only a packet contract, not private product data.
- Synthetic Golden Fixtures verify contracts and gate behavior, not real product
  correctness or Japan-market creative quality.
- Final semantic asset approval remains human/independent review; the wrapper
  cannot certify its own output.
