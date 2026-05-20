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
