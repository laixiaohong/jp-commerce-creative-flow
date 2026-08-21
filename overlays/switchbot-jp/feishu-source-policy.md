# Feishu Source Policy

## Formal scope

Feishu is a read-only Source Layer. Supported resource types are:

- Docx;
- Sheet;
- Bitable.

For a supplied URL, prefer the MCP tool `get_feishu_resource`. Do not infer that
authorization, search, a title-only result, or a connected plugin proves an
end-to-end resource read. A successful read must return the requested structured
content and source metadata.

If the tool is not exposed in the current runtime, mark `SOURCE_INTAKE_GATE` as
`BLOCKED` or use an explicitly approved read-only adapter. Never rename another
tool to imply that `get_feishu_resource` ran.

## Snapshot envelope

Normalize every read into a project-local snapshot containing:

- `source: feishu`;
- `resource_type`;
- `original_url`;
- `token`;
- title when returned;
- revision/updated time when returned, otherwise `null`;
- retrieval time;
- retrieval status and truncation/limit state;
- SHA-256 of the normalized content;
- structured content.

Sheet values remain two-dimensional. Bitable preserves tables, fields, records,
and pagination/truncation state. Do not flatten away row/field identity.

## Source grounding

Feishu content must pass normalization and Product Truth review before Planning.
Raw Feishu statements are not Approved Claims. Conflicts, partial reads,
permission failures, stale timestamps, and missing fields remain explicit.

## Storage

Store real snapshots outside this public repository. Do not commit access
tokens, credentials, internal URLs containing sensitive query data, raw source
content, or confidential attachments.
