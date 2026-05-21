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

## Evidence type

Customer signal is classified by what kind of evidence it provides:

- **Behavioral** — what respondents did. Observable. Example: switched tools, paid for a workaround, opened a GitHub issue, churned.
- **Attitudinal** — what respondents said they would do. Self-reported. Example: stated preference, hypothetical willingness to pay, opinion in an interview.

Attitudinal evidence predicts behavior at roughly 40–60% accuracy. A PRFAQ-grade conclusion requires behavioral corroboration; an attitudinal-only segment is `[assumption]` until behavior confirms it.

## Interview artifact type

`customer-interview-synthesis` distinguishes its inputs:

- **Transcript** — verbatim record of what was said. Weighted high.
- **Structured notes** — interviewer's filtered record. Weighted low; notes carry the interviewer's selection bias.
- **Survey response** — structured survey data. Weighted medium.

Treating transcripts and notes as interchangeable launders the interviewer's bias as customer signal.

## Gate decision

`launch-readiness-review` emits one of:

- `go` — all checks pass; launch.
- `no_go` — blocking drift, gaps, or risks; do not launch.
- `conditional_go` — launch with named conditions, each with its own owner and gate date.
- `defer` — the work isn't done; come back in N days. Distinct from `no_go` in that `defer` says "not yet, ask later," while `no_go` says "this should not ship as built."

`conditional_go` has historically rotted into soft `go`. Conditions must themselves be gated. A condition that says "we'll fix this post-launch" makes the decision `go-with-risk`, not `conditional_go`.

## PRFAQ drift severity

When `launch-readiness-review` compares the PRFAQ to the current build, each drift is rated:

- **Blocking** — the commitment isn't met; cannot ship.
- **Significant** — measurably different from promised; must be acknowledged in the launch narrative.
- **Acceptable** — within tolerance; documented but does not block.

## Risk status

How a risk from the PRFAQ risk register has evolved by launch time:

- **Mitigated** — the documented mitigation worked.
- **Open** — the risk still exists; mitigation unproven.
- **Materialized** — the risk happened during build; document the outcome.

## Tenet status

`tenets-review` rates each product tenet:

- **Valid** — external evidence still supports it.
- **Invalid** — external evidence contradicts it; thesis broken.
- **Unknown** — insufficient evidence to judge.

A tenet status check must cite external context (market shifts, competitor moves, regulatory changes), not just metrics. See the **metric satisficing** failure mode.

## Bet recommendation

`tenets-review` emits one of:

- `continue` — all tenets valid or unknown with active monitoring; keep investing.
- `kill` — one or more tenets invalid; stop investing.
- `pivot` — tenets need restatement; thesis has evolved.
- `escalate` — the decision is above this review's pay grade.

`continue` requires no tenet to be `invalid`. A single invalid tenet forces kill/pivot/escalate.

## Metric satisficing

A failure mode where output metrics sit within target while the underlying thesis has collapsed. Metrics keep saying "everything is fine" because the team has narrowed what they measure to what's still working. Caught by checking tenet validity against external context, not just metrics. The named risk that `tenets-review` exists to catch.

## Required reviews

Authoring skills declare a `required_reviews` field in their frontmatter listing reviewer skills that must run before the artifact is considered complete. Reviewer skills do not declare this field — they are the leaves. The convention converts the soft promise "if a reviewer is available, hand it the prose" into a contract. See [`SKILL_DESIGN_PATTERN.md`](SKILL_DESIGN_PATTERN.md#required-reviews).

## Constructive vs interrogative skills

Skills split by epistemic posture:

- **Constructive** skills produce an artifact (PRFAQ, six-pager, mechanism spec, WBR, CoE).
- **Interrogative** skills stress-test an artifact or belief and produce *revisions*, not new artifacts (linter, LP-reviewer, customer-interview-synthesis, launch-readiness-review, tenets-review).

Interrogative skills are the falsification layer. Users will be tempted to invoke them confirmatorily — to seek reassurance rather than friction. Skills in this category must refuse that posture explicitly in their stop conditions.
