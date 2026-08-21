# Claim Policy

## Separation

A product fact is not automatically an Approved Claim. Keep mechanism facts,
measured results, comparisons, rankings, launch decisions, and legal/marketplace
approval separate.

Raw Feishu content, competitor copy, reviews, KOL statements, planning drafts,
and AI-generated text cannot approve a claim.

## Approval record

An Approved Claim requires:

- exact consumer meaning and locale;
- product/offer/page scope;
- source references;
- conditions and test context when applicable;
- approval status;
- human approver identity;
- approval timestamp.

If any required field is absent, move the item to `unapproved_claims`. Do not
silently weaken or paraphrase it into an apparently approved claim.

## Forbidden behavior

- no automatic claim approval;
- no unsupported `No.1`, award, market-share, superiority, compatibility,
  performance, battery-life, AI, Matter, certification, price, or availability
  claims;
- no visual implication that exceeds the approved written meaning;
- no cross-SKU or cross-bundle claim leakage;
- no localization that changes fact, condition, or scope.

## Gate

`CLAIM_HUMAN_REVIEW_GATE` is always human-owned. Planning may prepare a review
queue, but Production receives only Approved Claims and explicit prohibitions.
