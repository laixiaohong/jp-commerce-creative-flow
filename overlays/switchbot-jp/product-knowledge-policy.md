# Product Knowledge Integration Policy

## Role

The existing `$product-knowledge` Skill is the normalized, governed product-fact
gate. Feishu is its discovery/evidence source. The Product Truth Packet is a
project-specific projection; it does not replace or update Product Knowledge.

## Resolution

1. Resolve the entity in `outputs/product_index.json` using identifier lookup or
   an exact normalized alias.
2. Keep `product_id`, `variant_id`, `bundle_id`, SKU, and Offer distinct.
3. Read the product knowledge page for orientation, then verify the canonical
   records required by `$product-knowledge`: product master/facts, Claim,
   compliance, known issues, and product profile; add price, compatibility,
   specification, positioning, competitor, or FAQ records only when needed.
4. Verify JP applicability, revision, review status, validity dates, firmware,
   dependencies, limitations, and unresolved conflicts.

Unknown or ambiguous entity resolution is `BLOCKED`; do not fuzzy-match it into
a known product.

## Mapping to Product Truth Packet

Map atomic records, not prose summaries:

| Product Knowledge | Product Truth Packet |
|---|---|
| master + identity | `product`, `sku_offers` |
| product facts/specs | `specifications`, `installation` |
| compatibility | `compatibility` |
| Claim records | `approved_claims`, `unapproved_claims`, `forbidden_claims` |
| pricing | `pricing` with channel/currency/tax/effective dates |
| bundle ownership | `bundles` and capability owner boundaries |
| positioning/VOC evidence | `target_users`, `user_scenarios` |
| source index + revisions | `sources` |
| conflicts/missing/stale | `unknown_tbd` and item status |

Every non-empty factual value retains a canonical `source_id`.

## Publish boundary

Structural validation does not approve external copy. An external Claim requires
both product-level external-publication readiness and an Approved Claim whose
source permits external use. `Conditional` keeps every condition. `Pending
Verification`, `Internal Only`, `Prohibited`, `Expired`, conflict, stale, and
unknown items stay out of consumer copy.

Price matching must preserve product, market, channel, price type, currency, tax
basis, and effective date. Missing price is not zero.

## Updates

If source review reveals an important new fact, conflict, or decision, update
Product Knowledge through its governed Change Set/review process. Do not write a
project packet back into canonical Product Knowledge and do not silently alter a
generated knowledge summary.
