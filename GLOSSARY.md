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

Risk register entries in PRFAQ, six-page-narrative, and launch-readiness-review carry both a severity and a likelihood. Named tiers with concrete anchors; numeric grids were rejected as theater.

**Severity** (consequence if the risk materializes):

- **catastrophic** — customer churn at scale, regulatory action, public incident, data loss
- **high** — significant rework, missed quarter commitment, named-customer escalation, contract violation
- **medium** — internal rework, slipped commitment within a team, recoverable operational pain
- **low** — documented, monitored, no immediate action; would be a footnote

**Likelihood** (probability the risk materializes in the review window):

- **likely** — historical base rate or current signal indicates this will happen
- **possible** — plausible based on adjacent evidence or named assumption
- **unlikely** — would require multiple unanticipated conditions to align
- **speculative** — no current evidence; included for completeness or stress-testing

A `proceed` recommendation paired with any `catastrophic + likely` or `catastrophic + possible` risk that lacks a documented mitigation is incoherent. Reviewers should fail it. Triage rules beyond that belong in the skills that use the scale, not in the scale itself.

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

## Calibration assessment

`ambitious-goal-grading` rates each goal not on attainment but on whether the *target* was set at the right level:

- **sandbagged** — hit at 100% with no surprise evidence; target was below honest capacity.
- **well_calibrated** — attainment in the honest range with cited plan or named surprises.
- **overreach** — missed badly because no plan could have hit the target (distinct from execution failure).
- **unknowable** — the team never stated difficulty intent; assessment is impossible.
- **goalpost_moving** — target moved mid-period and the grading hid the original; supersedes other classifications.

The named convention: 0.7 attainment is the honest norm, not 1.0. Borrowed from OKR practice.

## Attainment score

Continuous score (0.0–1.5) used by `ambitious-goal-grading`. Numeric goals: `actual / target`, clamped. Qualitative goals: `{met, partially_met, not_met}` maps to `{1.0, 0.5, 0.0}`. Over-attainment past 1.5 is itself a calibration signal.

## Pattern assessment

Cross-period calibration pattern from `ambitious-goal-grading`. Threshold is three consecutive periods of the same per-period assessment on the same recurring goal:

- **chronic_sandbagging** — triggers a `tenet_violation_candidate`; team is no longer testing the thesis.
- **chronic_overreach** — capacity, goal, or bet is mismatched to reality.
- **well_calibrated** — baseline.
- **mixed** — no clean pattern.
- **insufficient_data** — only valid when prior gradings genuinely absent.

## Goal-setting context

The team's stated difficulty intent at authoring time: `committed`, `stretch`, `aspirational`, or `unstated`. Without it, every outcome can be retroactively framed as success. `unstated` is itself a finding.

## Sandbagging laundering

The named failure mode `ambitious-goal-grading` exists to catch. Targets set deliberately or implicitly below honest capacity and described in language that sounds principled: "ambitious enough to motivate, achievable enough to hit." Detected by the rule that any 100% attainment without cited surprise evidence is presumptive sandbagging until proven otherwise. Analogous in structure to `metric satisficing` for `tenets-review` — both are failure modes where the surface signal looks healthy while the underlying mechanism has stopped working.

## Dissent recommendation

`dissent-before-commit` emits one of:

- `proceed` — strongest dissent addressed in the action OR accepted with a named tradeoff.
- `proceed_with_changes` — named changes required before the action fires.
- `pause` — action does not fire; trigger conditions must resolve first.
- `escalate` — decision is above this review's pay grade; named target gets a briefing.

`proceed` on a one-way door requires `addressed_in_action: true`. Accepted tradeoff is insufficient for irreversible actions.

## Reversibility (one-way / two-way door)

Borrowed from Bezos. Used by `dissent-before-commit` to control how strict the dissent gate is:

- **One-way door** — action is not reversible without significant cost. The team owns the outcome once executed. Examples: production data migrations without rollback paths, public announcements, hires/fires, deprecation cut-overs. Dissent must be *addressed in the action* — accepted tradeoff is insufficient.
- **Two-way door** — action is reversible at modest cost within a reasonable timeframe. Examples: feature flag rollouts, internal UI changes, batch job schedule changes. Addressed OR accepted-with-named-tradeoff is sufficient.
- **Partial reversal** — reversible but with material cost or partial recovery only. Examples: schema change with backfill cost, multi-tenant config change with per-tenant unwind. Treat closer to one-way door; accepted tradeoff requires a named owner of the reversal cost.

## Dissent perspective

`dissent-before-commit` requires a *named functional perspective* on each dissent item. Generic "the team" or "people" fails the gate. The default perspective set: engineering, operations, support, customer-facing, security, finance, compliance. Choice is by stake, not by checklist — canvassing all seven on every action is itself a rubber-stamp pattern. See [`skills/12-dissent-before-commit/dissent-perspectives.yaml`](skills/12-dissent-before-commit/dissent-perspectives.yaml) for typical stakes and dissent patterns per perspective.

## Stale dissent reuse

The named failure mode `dissent-before-commit` exists to catch. The team points to authoring-time dissent (six-pager's gate, LP-reviewer's `are_right_a_lot`) as proof that concerns were heard, and proceeds with execution without checking what has changed between authoring and now. The dissent record was true at authoring time and may be stale now — state changes since authoring may have invalidated prior assessments or surfaced concerns that weren't visible then. The skill's `dissent_recanvassed` gate exists to force re-evaluation against current state. Analogous in structure to `metric satisficing` (tenets-review) and `sandbagging laundering` (ambitious-goal-grading) — each names a way a previously-honest signal goes stale while looking healthy.

## Portfolio bet recommendation

Per-bet recommendation emitted by `portfolio-review` for each currently-funded bet. One of `continue` | `wind_down` | `amplify` | `hold` | `pivot`. Distinct from `tenets-review`'s `bet_recommendations` (which is per-bet thesis validity); `portfolio_bet_recommendation` is a cross-bet allocation decision informed by tenets-review but not equivalent to it. `continue` requires the same evidentiary burden as `wind_down` or `amplify` — status-quo defense is not free.

## Candidate decision

Per-candidate-alternative decision emitted by `portfolio-review` for each item in the backlog of unfunded bets. One of `fund` | `continue_to_park` | `reject`. A `fund` decision requires a named `opportunity_cost_against` — which current bet's allocation gets drawn from to fund the candidate. Candidates parked across multiple consecutive reviews trigger the *quiet candidate parking* drift pattern; the skill escalates rather than letting candidates accumulate.

## Allocation change severity

How significant a drift between the actual portfolio and the zero-based hypothetical portfolio is, used in `portfolio-review`'s `drift_detected` output. `blocking` means the zero-based check fails materially and the portfolio must change this period; `significant` means drift is named and acknowledged; `acceptable` means drift is within tolerance and documented.

## Portfolio drift

The named failure mode `portfolio-review` exists to catch. The portfolio that exists now is the residue of accumulated past decisions, not the portfolio anyone would intentionally author today. Each bet was individually justified at some point; the collective allocation no longer is. The surface signal — stable composition, defensible per-bet stories, total spend consistent with last period, no bet killed in 6+ months — hides incoherent marginal allocation: bets that should be wound down continue because killing them is socially expensive; bets that should be amplified aren't because reallocation is operationally expensive; candidates sit parked indefinitely because deciding either way costs political capital. The skill's second-axis check is the **zero-based reallocation** — if you were authoring this portfolio from scratch today with the same total capacity, what would it look like? Bets that don't survive a zero-based authoring are portfolio drift candidates. Specific sub-patterns include halo allocation, sunk-cost drift, diversification theater, founder flagship protection, quiet candidate parking, scope creep as amplification, and kill-list theater; see [`skills/13-portfolio-review/allocation-patterns.yaml`](skills/13-portfolio-review/allocation-patterns.yaml). Analogous in structure to the other named failure modes in this index.

## Founder bias laundering

The named failure mode `customer-interview-synthesis` exists to catch. The founder's prior is dressed up as customer signal by a panel that was selected, recruited, or questioned in ways that pre-loaded the answer. The surface signal — interview themes align with the founder's hypothesis — hides that the methodology made the alignment near-inevitable. The skill's second-axis check is the requirement that `evidence_against` for the founder's hypothesis be non-empty (its emptiness is itself flagged), combined with bias-pattern citations against `selection_method` and `interview_method` per [`skills/08-customer-interview-synthesis/bias-patterns.yaml`](skills/08-customer-interview-synthesis/bias-patterns.yaml). Specific sub-patterns include friend-panel blindness (cohort recruited from the founder's network), leading questions, attitudinal-only segments, solution-first framing, and synthesis as confirmation. Analogous in structure to `metric satisficing`, `sandbagging laundering`, `stale dissent reuse`, and `PRFAQ drift` — each names a way a previously-honest signal looks healthy while the underlying mechanism has stopped working (or, in this case, never produced honest signal to begin with).

## PRFAQ drift

The named failure mode `launch-readiness-review` exists to catch. The gap between what the PRFAQ promised at authoring time and what the build actually delivers at launch time. The surface signal — features shipped match the PRFAQ scope, the team is on the original timeline, the contract was approved — hides that the planned features do not produce the promised customer outcome, or that scope crept silently between authoring and launch, or that the risk register's mitigations have decayed. The skill's second-axis check is the `customer_outcome_assessment` gate: a scope match is not a customer-outcome match. Specific sub-patterns include scope-match satisficing (the canonical instance — confirming features-shipped against features-promised and stopping there), narrative laundering (launch narrative obscures drift), and PRFAQ-as-stale-artifact rationalization (ignoring the contract because it is "old"). Analogous in structure to the other named failure modes in this index.

## Named failure modes (cross-reference)

The suite has a signature architectural commitment: every interrogative skill that gates an artifact's *ongoing validity over time* declares a single named failure mode it exists to catch. Each instance has a specific name, but they share a shape:

> A surface signal that looks healthy on its face masks a structural failure underneath. The skill refuses to grade only against the surface; it forces a second-axis check.

Current instances:

| Skill | Named failure mode | Surface signal | Second-axis check |
|---|---|---|---|
| [`customer-interview-synthesis`](#founder-bias-laundering) | **founder bias laundering** | interview themes align with founder's hypothesis | forced `evidence_against` + bias-pattern citations against selection/interview method |
| [`launch-readiness-review`](#prfaq-drift) | **PRFAQ drift** | features shipped match PRFAQ scope | `customer_outcome_assessment` — scope match is not customer-outcome match |
| [`tenets-review`](#metric-satisficing) | **metric satisficing** | output metrics within target | external context (market, competitor, regulatory shifts) |
| [`ambitious-goal-grading`](#sandbagging-laundering) | **sandbagging laundering** | attainment hits at 100% | surprise evidence + stated difficulty intent |
| [`dissent-before-commit`](#stale-dissent-reuse) | **stale dissent reuse** | authoring-time dissent record exists | re-canvass against `state_changes_since_authoring` |
| [`portfolio-review`](#portfolio-drift) | **portfolio drift** | stable composition, defensible per-bet stories | zero-based reallocation — would the portfolio be re-authored today? |

Interrogative skills that gate an artifact's *initial quality* (`amazon-writing-linter`, `leadership-principles-reviewer`) do not declare a named failure mode of this shape — their failures are local to the artifact under review, not products of time passing or methodological pre-loading.

See [`SKILL_DESIGN_PATTERN.md`](SKILL_DESIGN_PATTERN.md#named-failure-modes) for the rule that new ongoing-validity interrogative skills must declare one of these.

## Required reviews

Authoring skills declare a `required_reviews` field in their frontmatter listing reviewer skills that must run before the artifact is considered complete. Reviewer skills do not declare this field — they are the leaves. The convention converts the soft promise "if a reviewer is available, hand it the prose" into a contract. See [`SKILL_DESIGN_PATTERN.md`](SKILL_DESIGN_PATTERN.md#required-reviews).

## Constructive vs interrogative skills

Skills split by epistemic posture:

- **Constructive** skills produce an artifact (PRFAQ, six-pager, mechanism spec, WBR, CoE).
- **Interrogative** skills stress-test an artifact or belief and produce *revisions*, not new artifacts (linter, LP-reviewer, customer-interview-synthesis, launch-readiness-review, tenets-review).

Interrogative skills are the falsification layer. Users will be tempted to invoke them confirmatorily — to seek reassurance rather than friction. Skills in this category must refuse that posture explicitly in their stop conditions.
