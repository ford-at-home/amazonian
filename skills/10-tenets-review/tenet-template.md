# Tenet Template

A **tenet** is an "if we're wrong about X, stop" statement. Tenets are written when the bet is authorized (in the PRFAQ) so that future tenets-reviews have something falsifiable to check against. A bet without written tenets is a bet that cannot be honestly killed — the team will always find metrics to justify continuing.

This template is meant to live alongside the PRFAQ, not as a separate artifact. Add a `## Tenets` section to the PRFAQ using this structure.

---

## Tenets — `<bet name>`

Authored: `<date>` by `<author>`
Last reviewed: `<date>` via `tenets-review`

---

### Tenet 1: `<short label>`

**Statement.** If we are wrong about `<specific claim about the customer, market, or technology>`, we should stop investing in this bet.

**Why this is the right tenet.** `<one paragraph: what this claim is load-bearing for; what collapses if it's wrong>`

**What evidence would falsify this tenet?**

- `<specific external signal>` — `<source where this would show up>`
- `<specific customer behavior>` — `<source>`
- `<specific market or competitive move>` — `<source>`

**What this tenet is NOT.** `<one sentence: explicitly rule out adjacent claims to prevent scope creep when the tenet is reviewed>`

**Owner.** `<named individual responsible for monitoring external evidence against this tenet>`

---

### Tenet 2: `<short label>`

*(same structure)*

---

### Tenet 3: `<short label>`

*(same structure)*

---

## Rules for writing tenets

- **Three to five tenets, not ten.** A bet with ten tenets has none — every metric will partially support at least one and the team will always continue.
- **Each tenet must be falsifiable by external evidence, not by internal metrics.** "Customers will love it" is not a tenet; "competitor X will not ship a free version in 18 months" is.
- **Each tenet must be specific.** "We need product-market fit" is not a tenet. "Engineering managers at companies with 25–100 engineers will pay $19/seat/month for weekly status digest" is.
- **Each tenet must have a named owner** responsible for monitoring its validity, separate from the bet's owner. Owners marking their own tenets fail at the same rate as owners marking their own homework.
- **Each tenet must include "what is NOT this tenet"** to prevent scope shrinkage at review time. The most common review failure is narrowing the tenet to whatever the metrics support.

## What disqualifies a tenet

- It is a metric, not a belief. ("MRR must grow 10% MoM" is a metric, not a tenet. The tenet behind it is what *makes the metric possible*.)
- It is a vague aspiration. ("We will delight customers.")
- It cannot be falsified by anything observable. ("Customers want better software.")
- It is the founder's hypothesis restated. ("This is a good idea.")
- It was added because someone said "should we have a tenet about X?" — tenets are load-bearing, not exhaustive.

## Using this template at review time

`tenets-review` will read the `## Tenets` section directly. If this section is missing from the PRFAQ, the review skill will synthesize tenets from `decision_recommendation.rationale` and flag them with `needs_ratification: true`. Synthesizing is a degraded mode — written tenets are always preferred.

A tenet flagged `needs_ratification` cannot drive a `kill` or `pivot` recommendation until the team ratifies it. This is the only safety valve against the review skill killing a bet on tenets the team never agreed to.
