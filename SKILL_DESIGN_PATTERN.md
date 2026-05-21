# Skill Design Pattern

Every skill in this suite conforms to the same spine. The point is to make agents *predictable* and *inspectable*, not creative. If a skill cannot satisfy the fields below, it does not belong in this suite.

## The spine

```yaml
skill:
  name:                       # kebab-case, max 64 chars
  purpose:                    # one sentence; the customer outcome
  inputs:                     # everything the skill needs from the user, named and typed
  required_artifacts:         # files, configs, or data the skill must read before producing output
  process_steps:              # ordered, deterministic steps the skill follows
  validation_gates:           # hard checks that must pass before the skill emits output
  reviewer_agent:             # what another agent (or another pass) checks before final emit
  output_schema:              # structured shape of the output, named and typed
  failure_modes:              # known ways this skill is wrong, with countermeasures
  stop_conditions:            # cases where the skill refuses to produce output
  follow_up_mechanism:        # what naturally comes next; how the skill hands off
```

## Rationale per field

- **name / purpose** — discoverable. If the agent cannot tell when to invoke the skill from the description alone, the skill is too vague.
- **inputs** — explicit, named, typed. Never have a skill that takes "context" as a parameter.
- **required_artifacts** — declares the dependency on prior work. A skill that reads `prfaq.md` should say so.
- **process_steps** — ordered. Resistance to ordering is usually a signal the skill is doing too much.
- **validation_gates** — the most important field. These are the mechanisms that prevent the skill from emitting confident garbage. A skill without gates is a wish.
- **reviewer_agent** — a second pass over the draft. Can be a reviewer skill (e.g. `leadership-principles-reviewer`), a linter (`amazon-writing-linter`), or an explicit self-check. Without it, the skill marks its own homework.
- **output_schema** — structured. Free-form markdown is fine; unstructured markdown is not. Every skill emits something a downstream skill can consume.
- **failure_modes** — name the way it is going to go wrong. If the author cannot name a failure mode, they do not understand the skill yet.
- **stop_conditions** — bright lines. "If X, refuse and ask the user." This is what stops the skill from inventing context.
- **follow_up_mechanism** — names the next artifact in the operating system. No skill is a leaf node.

## What disqualifies a candidate skill

A proposal does not belong in this suite if:

- It has no validation gates (i.e., it always emits something).
- Its only output is "advice" or "considerations" with no required structure.
- It cannot name a failure mode.
- It cannot name a downstream artifact or skill that consumes its output.
- It collapses into "be thoughtful." That is not a mechanism. That is a vibe.

## Tone

Skills in this suite are written for agents to *follow*, not for humans to *enjoy*. Dryness and minor humor are fine in human-facing READMEs and rationale sections. Inside the instructions, prefer flatness; an LLM should not have to guess whether a sentence is sincere.

## Length

Hard limit: `SKILL.md` body under 500 lines. Soft target: under 250. Push detail into templates, rules, and examples adjacent to the skill, not into the `SKILL.md` itself.

## Assumption tagging

Every claim a skill emits should be tagged with one of:

- `[fact]` — verifiable, with a source
- `[assumption]` — believed true, untested
- `[inference]` — derived from facts above
- `[open question]` — listed in an explicit Open Questions section

A skill that emits unlabeled claims is producing confident fog. Add the tags.

Canonical definitions live in [`GLOSSARY.md`](GLOSSARY.md#assumption-tags); machine-readable form in [`vocabulary.yaml`](vocabulary.yaml).

## Required reviews

Authoring skills must declare which reviewer skills must run before their artifact is considered complete. This goes in the skill's YAML frontmatter:

```yaml
---
name: working-backwards-prfaq
description: ...
required_reviews:
  - amazon-writing-linter
  - leadership-principles-reviewer
---
```

The skill's `## Process` section must include a step that invokes each required reviewer. The skill's `## Validation gates` must include a gate that fails if any required review has not been completed.

Reviewer skills (those whose output is feedback rather than an artifact) do not declare `required_reviews`. They are the leaves.

The convention exists because reviewer cadence is the suite's leverage. A reviewer that is optional becomes decorative.

## Constructive vs interrogative

Each skill belongs to one of two epistemic categories:

- **Constructive** — produces an artifact (PRFAQ, six-pager, mechanism, WBR, CoE).
- **Interrogative** — stress-tests an artifact or belief and produces revisions, not new artifacts (linter, LP-reviewer, customer-interview-synthesis, launch-readiness-review, tenets-review, ambitious-goal-grading, dissent-before-commit, portfolio-review).

Interrogative skills are the falsification layer. They must refuse confirmatory invocation explicitly in their stop conditions. A reviewer asked to "confirm this is good" is being asked to fail at its job.

## Named failure modes

Interrogative skills that gate an artifact's **ongoing validity over time** must declare a single named failure mode they exist to catch. Each instance has a specific name, but they share a shape:

> A surface signal that looks healthy on its face masks a structural failure underneath. The skill refuses to grade only against the surface; it forces a second-axis check.

Current instances (see [`GLOSSARY.md#named-failure-modes-cross-reference`](GLOSSARY.md#named-failure-modes-cross-reference)):

- `customer-interview-synthesis` → **founder bias laundering**
- `launch-readiness-review` → **PRFAQ drift**
- `tenets-review` → **metric satisficing**
- `ambitious-goal-grading` → **sandbagging laundering**
- `dissent-before-commit` → **stale dissent reuse**
- `portfolio-review` → **portfolio drift**

**The rule for new skills:**

If a proposed interrogative skill gates ongoing validity (anything where a previously-valid signal can become stale or misleading over time), it must declare a named failure mode with:

1. A short, concrete name (two or three words, not a sentence).
2. The surface signal the failure mode hides behind.
3. The second-axis check the skill performs to refuse grading on surface alone.

If a proposed interrogative skill gates only **initial quality** of an artifact (e.g., prose linting, principle review) — its failures are local to the artifact under review and not products of time passing — a named failure mode is not required.

The named failure mode goes in the skill's frontmatter `description`, in a `## Failure modes` section, and in `GLOSSARY.md`. The cross-reference index in `GLOSSARY.md` is the single surface for discovering the pattern.

**Why this matters.** Surface signals are easy to engineer (or accidentally produce) so they keep looking healthy after the underlying mechanism has stopped working. Without a named failure mode and a second-axis check, an interrogative skill becomes a confirmation engine. The named failure mode is the load-bearing commitment that the skill refuses to be one.
