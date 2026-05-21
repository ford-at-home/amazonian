---
name: six-page-narrative
description: Convert a strategy, architecture, or major decision into a six-page narrative — a written decision memo with context, problem, current state, proposed mechanism, alternatives, risks, metrics, and explicit dissent. No slides. No bullet soup. Use when preparing a decision document for senior review, when an architecture needs written defense, or when the user mentions "six-pager", "narrative", "decision memo", "strategy doc", or "ADR but bigger".
category: constructive
required_reviews:
  - amazon-writing-linter
  - leadership-principles-reviewer
---

# Six-Page Narrative

Produce a written decision memo that argues for a specific recommendation, surfaces hidden assumptions, and includes a dissent section. No slides. Bullet points only when summarizing, never when making an argument.

## Quick start

1. Collect the inputs below.
2. Use [`template.md`](template.md) as the section skeleton.
3. Draft in prose. Force causal logic ("because X, therefore Y").
4. Make assumptions explicit and tag every empirical claim.
5. Solicit and record dissent.
6. Hand the draft to `amazon-writing-linter`, then to `leadership-principles-reviewer`.

## When to use

- A decision is significant enough that "let's discuss in a meeting" is insufficient.
- An architecture proposal needs written defense.
- A strategy shift needs senior alignment.
- The user mentions: "six-pager", "narrative", "decision memo", "ADR".

## When NOT to use

- A product or feature idea is still being defined. Use `working-backwards-prfaq` first; the PRFAQ feeds the narrative.
- The artifact needed is a recurring operational mechanism. Use `mechanism-designer`.
- The work is a post-incident review. Use `correction-of-errors`.

## Inputs

```yaml
decision_needed:              # the specific decision the reader must make
context:                      # what the reader needs to know to evaluate this
problem:                      # the customer or business problem being solved
current_state:                # what exists today, including its failure modes
proposed_mechanism:           # the proposed change
alternatives_considered:      # at least 2, each with why-rejected
risks:                        # known risks with severity, likelihood, mitigation, owner
                              # severity + likelihood use the canonical scales in
                              # vocabulary.yaml#severity_and_likelihood
                              # (severity: catastrophic|high|medium|low;
                              #  likelihood: likely|possible|unlikely|speculative)
metrics:                      # how success and failure will be measured
dissent:                      # named individuals who disagree, and why
appendix:                     # supporting data, prior art, links
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Decision is specific | A single sentence answers "what is the reader being asked to decide?" | Rewrite |
| Alternatives are real | At least two alternatives, each with a documented reason for rejection | Add real alternatives |
| Causal logic | Every "therefore" is preceded by a stated cause | Restructure |
| Dissent recorded | Either named dissenters with their position, or a stated reason no dissent exists | Solicit dissent |
| Hidden assumptions surfaced | Every `[assumption]` tag is also listed in an Assumptions register | Re-scan |
| No slide thinking | No section is bullet-only; no bullet exceeds two clauses | Rewrite as prose |
| Required reviews completed | `amazon-writing-linter` and `leadership-principles-reviewer` have both run against the draft and their revisions are incorporated | Run them; do not emit |

## Process

1. **Collect** inputs.
2. **Draft** in order: Decision → Context → Problem → Current State → Proposed Mechanism → Alternatives → Risks → Metrics → Dissent → Appendix.
3. **Audit** for causal logic. Each "because" and "therefore" should hold up to a reviewer asking "why?".
4. **Surface** hidden assumptions. Move them from the prose into the Assumptions register.
5. **Record** dissent. Talk to a named dissenter, or write down why no one disagrees and from whom you sought disagreement.
6. **Lint** with `amazon-writing-linter` before final review.

## Output schema

Sections, in order:

1. Context
2. Customer / User Problem
3. Current State
4. Proposed Mechanism
5. Alternatives Considered
6. Risks and Mitigations
7. Metrics
8. Dissent
9. Decision Needed
10. Appendix

See [`template.md`](template.md) for the prose skeleton.

## Stop conditions

- The user cannot name the specific decision the reader must make.
- "Alternatives considered" contains fewer than two alternatives, or the rejected alternatives were never seriously considered.
- The proposed mechanism is "be better at X" rather than a specific change with cadence, inputs, and outputs.

## Failure modes

- **Bullet soup.** A narrative collapses into bullet lists in the body. Rewrite as prose; reserve bullets for summary or enumeration.
- **Straw alternatives.** Listed only to be dismissed. Steel-man them before rejecting.
- **Risk-washing.** Every risk has "we will monitor" as the mitigation. Demand specific mitigations with owners.
- **Dissent omission.** If everyone agrees, that is itself a risk signal. Note it.
- **The two-page narrative pretending to be six.** Padding does not deepen a thin argument; it hides it.

## Follow-up mechanism

- After this skill, run `amazon-writing-linter` then `leadership-principles-reviewer`.
- Metrics defined here feed into `weekly-business-review`.
- Recurring operational pieces of the proposed mechanism feed into `mechanism-designer`.

## Handoffs

**Consumes from**

- `working-backwards-prfaq` (optional): `success_metrics` → `metrics`; `risks` → `risks`; `mvp_boundary` → `current_state` context
- User inputs.

**Feeds into**

- `amazon-writing-linter`: section prose → `draft` (mandatory pass before review)
- `leadership-principles-reviewer`: full memo → `proposal` (`proposal_type: six_pager`)
- `mechanism-designer`: "Proposed Mechanism" section → `goal` + `desired_behavior`
- `weekly-business-review`: "Metrics" section → `input_metrics` / `output_metrics` (labeled per [`GLOSSARY.md`](../../GLOSSARY.md#input-vs-output-metrics))
- `dissent-before-commit`: full memo → `authoring_artifact`; dissent section → `dissent_history`

Enums used: `decision_recommendation`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
