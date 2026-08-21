# Operating Guide

## Normal use

From a Codex workspace where the Skill is installed, invoke:

```text
$jp-commerce-creative-flow
```

Then provide the product/project name, target channel, offer scope, and source
links/files. The entry performs Source Intake and Product Truth setup before it
routes into the upstream listing stages.

## Runtime storage

Create a private project directory outside this public repository:

```text
<project>/source-snapshots/
<project>/product-truth/
<project>/planning/
<project>/production/
<project>/hardening/
```

Never commit real Feishu content, prices, approvals, assets, or unreleased facts
to the public fork.

## Feishu intake

1. Call the read-only MCP `get_feishu_resource` for each Docx, Sheet, or Bitable
   URL.
2. Confirm the requested structured content was returned; authentication alone
   is not proof.
3. Save the raw result in the private project workspace.
4. Normalize it:

```bash
python overlays/switchbot-jp/scripts/normalize_feishu_resource.py \
  <raw-result.json> <project>/source-snapshots/<source>.json
```

5. Review truncation, freshness, conflict, and source scope.

## Build and lock Product Truth

First invoke/read `$product-knowledge`, resolve the exact product/variant/bundle,
and verify the canonical records required for the task. Map atomic records and
their source IDs into a human-reviewed intake matching the Product Truth Packet
schema, then:

```bash
python overlays/switchbot-jp/scripts/build_product_truth_packet.py \
  <reviewed-intake.json> \
  <project>/product-truth/product-truth-packet.json \
  --lock <project>/product-truth/product-truth-packet.lock.json

python overlays/switchbot-jp/scripts/validate_product_truth_packet.py \
  <project>/product-truth/product-truth-packet.json \
  --lock <project>/product-truth/product-truth-packet.lock.json
```

The builder demotes any claimed “approved” item whose human approval record is
incomplete. Resolve issues in the reviewed intake and create a new revision;
do not edit a frozen packet in place.

## Checkpoints

The normal review sequence is:

1. Product Truth and open conflicts;
2. consumer/market strategy;
3. Amazon page plan and Gallery/A+ storyline;
4. first representative visual direction;
5. produced asset set;
6. exact-file evidence and assembled Demo;
7. final human visual approval.

## Upstream updates

The scheduled workflow creates a Draft PR only. It never merges to `main`.

Before enabling it, set repository Actions workflow permissions to allow
read/write contents and pull requests. Every sync PR contains a compatibility
report and must pass both upstream and Overlay regression tests.

Human review must check:

- protected five-Skill files changed by upstream;
- Product Truth/claim semantics;
- Gallery/A+ contracts and module limits;
- validator/gate behavior;
- packaging and install behavior;
- all three Golden Fixtures.

Merge only after review. If merge conflicts occur, the workflow stops and a
maintainer resolves them manually on the sync branch.
