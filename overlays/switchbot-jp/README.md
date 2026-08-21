# SwitchBot JP Overlay

This directory contains the business customization layer for the public
`japan-listing-demo` core.

```text
Upstream Core + SwitchBot JP Overlay = JP Commerce Creative Flow
```

The Overlay is additive. It does not fork internal stage logic and contains no
real Feishu data, confidential product facts, prices, approvals, or assets.

Runtime project data must live outside this public repository. Use the scripts
in `scripts/` to normalize Feishu output and build/validate a locked Product
Truth Packet before handing work to `$japan-listing-demo`.
