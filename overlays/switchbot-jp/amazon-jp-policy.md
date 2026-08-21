# Amazon JP Policy

Use the upstream `listing-planning` Amazon.co.jp profile as the channel core.
This Overlay adds SwitchBot JP operating rules without replacing that profile.

## Page logic

Design around the shopper decision path:

```text
Search → Main Image → Title/Bullets → Gallery → Comparison → A+ → Review/FAQ
```

Do not allocate one image per feature. Every Gallery/A+ role must state the
consumer question, communication objective, approved message, proof object,
visual structure, and required source asset.

Gallery-native and enhanced-content roles stay separate unless Planning
explicitly authorizes a derivative and Hardening verifies the exact result.

## Module budget

Use the upstream packaged channel-policy limit as the machine authority. The
current packaged ceiling is Basic A+ 5 modules and Premium A+ 7 modules, with
Brand Story separate. Account/category availability must still be verified for
the actual project; the Overlay may lower but never raise the upstream ceiling.

## Japan review

Consumer-visible Japanese requires native review for naturalness, ambiguity,
terminology, claim conditions, mobile comprehension, and marketplace fit.

Do not infer Amazon account capabilities from competitor pages.
