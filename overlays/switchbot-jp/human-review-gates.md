# Human Review Gates

## Required gates

| Gate | Human decision | Automation may do | Automation must not do |
|---|---|---|---|
| Product Truth review | Resolve conflicts and approve project baseline | Validate structure, sources and hash | Invent or resolve product facts |
| Claim review | Approve exact claim meaning, locale, scope and conditions | Build review queue | Approve or broaden a claim |
| Strategy checkpoint | Approve target, positioning, page plan and storyline | Check completeness and consistency | Treat silence as approval |
| Visual direction | Approve the initial representative asset/direction | Produce a review artifact | Start unrestricted batch production |
| Exact asset review | Approve exact hash + role + scope | Fingerprint and reconcile evidence | Transfer approval to changed bytes |
| Final visual review | Approve the verified assembled delivery | Run QA and parity checks | Auto-approve final visuals or publish |

## Recording

Every approval record contains approver, timestamp, decision, object ID, exact
scope, and exact file hash where applicable. `继续` advances routing but does not
equal Claim or final visual approval unless the user explicitly approves that
object.

## Release boundary

Automation may prepare a Draft PR, review packet, or delivery candidate. Merge,
external publication, channel upload, and final visual approval remain human
actions.
