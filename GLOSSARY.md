# Glossary

Definitions of terms used across the skills suite. The canonical machine-readable form lives in [`vocabulary.yaml`](vocabulary.yaml); this file is the human-readable companion.

Skills reference these definitions rather than restate them.

## Assumption tags

Every empirical claim a skill emits should be tagged with one of:

- `[fact]` — verifiable, with a source.
- `[assumption]` — believed true, untested.
- `[inference]` — derived from facts already established.
- `[open question]` — listed in an explicit Open Questions section.

Untagged claims are confident fog. Add the tags.

## Variance classifications

Every negative variance in a Weekly Business Review must map to exactly one of:

- Known cause
- Hypothesis
- Unknown
- No action needed because…
- Action item created

"Unknown" is acceptable for one week. Two weeks of "unknown" on the same metric is a process failure and should trigger `correction-of-errors` on the inspection mechanism itself.

## Input vs output metrics

- **Input metric** — a leading indicator the team controls. Example: number of customer interviews completed this week.
- **Output metric** — a lagging indicator the customer experiences. Example: customer-reported time-to-status.

Skills that ask for metrics (`weekly-business-review`, `mechanism-designer`) require both. Skills that emit metrics (`working-backwards-prfaq`, `six-page-narrative`) should label each metric as input or output.

## Decision recommendation

The terminal recommendation emitted by an authoring skill is one of:

- `proceed`
- `proceed_with_changes`
- `do_not_proceed`
- `needs_more_info`

A `proceed` recommendation paired with high-severity unmitigated risks is incoherent; reviewers should fail it.

## Principle score

In a leadership-principles review, each principle is scored:

- **strong** — cited evidence in the proposal.
- **weak** — mentioned without evidence, or evidence runs counter.
- **silent** — the proposal does not address this principle.
- **contradictory** — the proposal invokes this principle to skip another (e.g., bias-for-action used to justify skipping dive-deep).

If every principle scores "strong", the review is failing.

## Blameless

In a Correction of Errors, **blameless** means: no section names an individual as the cause. Roles and systems carry the analysis. The point is not to absolve individuals — it is to surface the system conditions that allowed the human action to produce customer impact.

## Decision relevance

A section has **decision relevance** if it answers "so what?" within itself. A paragraph that summarizes activity without naming what the reader should decide or do has no decision relevance and should be cut or rewritten.

## MVP boundary

The explicit list of what is in scope and what is *not*. Out-of-scope must contain at least three plausible items — items that someone could reasonably have expected to be included. A boundary that excludes only "impossible" things is not a boundary.

## Severity and likelihood

`[open question]` — PRFAQ and six-page-narrative both ask for severity and likelihood on each risk, but neither defines the scale. Pick one consistently within a document and document the choice. This is a known gap to close in a follow-up.
