---
name: amazon-writing-linter
description: Rewrite docs into clear, evidence-heavy Amazon-style prose. Strips vague adjectives, unsupported claims, passive evasions, and weasel words; demands metrics, owners, and decision relevance. Use when polishing a PRFAQ, six-page narrative, memo, or any decision-bearing document; when the user asks to "tighten", "edit", or "make this Amazon-style"; or when a draft is full of "we believe", "significant", "robust", or "simple".
---

# Amazon Writing Linter

Rewrite a draft into clear, evidence-heavy prose. Surface every claim that needs evidence. List every owner, action, and date promised but not specified.

This skill is opinionated. It is closer to a compiler than to an editor: it refuses to emit prose that violates the rules in [`rules.yaml`](rules.yaml).

## Quick start

1. Read the draft.
2. Classify each sentence against the rules in [`rules.yaml`](rules.yaml).
3. Rewrite the prose into the structured output below.
4. Emit unfixable claims as Open Questions; do not silently strip them.

## When to use

- A draft is ready for review and needs to be tightened before submission.
- The user mentions: "tighten", "edit", "rewrite in Amazon style", "remove fluff", "make this evidence-based".
- The draft is full of weasel words, hedging, or unsupported confidence.
- A PRFAQ or six-page narrative has been drafted and needs a linting pass before reviewer review.

## When NOT to use

- The draft has not been written yet. Use `working-backwards-prfaq` or `six-page-narrative` to draft first.
- The artifact is a private note or stream-of-thought; the linter assumes the prose is intended for a reviewer.
- The goal is to make the prose more persuasive. This skill makes prose more *honest*, which is sometimes the opposite.

## Inputs

```yaml
draft:                        # the raw prose
audience:                     # who reads this; affects what "decision relevance" means
known_facts:                  # optional list of facts the rewriter can cite without flagging
```

## Rules

The full rule set lives in [`rules.yaml`](rules.yaml). Summary:

### Reject (require rewrite)

- Vague adjectives without a metric ("significant", "robust", "best-in-class", "scalable").
- Unsupported claims ("customers love it", "much better").
- Passive evasions ("mistakes were made", "issues occurred").
- "We believe" without evidence.
- "Simple" unless qualified by what makes it simple.
- Marketing copy in places that should be prose ("seamless", "delight", "magical").
- Pronouns with no antecedent ("they decided", "it works").

### Require

- Concrete subject (who).
- Concrete verb (did what).
- Metric or evidence where the claim is empirical.
- Decision relevance ("so what?").
- Owner, action, and date for every commitment.

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Every claim tagged | Each empirical statement carries `[fact]`, `[assumption]`, `[inference]`, or `[open question]` | Add tags |
| Commitments have owner + date | "We will" sentences include who and when | Demand them |
| No banned words remain | None of the words in `rules.yaml: reject` survive in the rewrite | Rewrite |
| Decision relevance | Each section answers "so what?" within itself | Rewrite or strike |

## Process

1. **Parse** the draft into sentences.
2. **Classify** each sentence: keep / rewrite / strike / flag for evidence.
3. **Rewrite** keeping the original meaning where possible.
4. **List** every claim that needs evidence (separate from rewrites).
5. **List** every word or phrase stripped (so the author can verify nothing important was lost).
6. **Emit** the structured output below.

## Output schema

```markdown
## Rewritten Version

<the cleaned prose>

## Claims That Need Evidence

- <claim>: <why it needs evidence>

## Removed Fluff

| Original | Reason removed |
|----------|----------------|
|          |                |

## Open Questions

- <question>: owner? deadline?

## Decision-Relevant Summary

<3–5 sentences. What is the reader being asked to decide or do?>
```

## Stop conditions

- The draft is fewer than three sentences (too little to lint).
- The draft is a personal note or journal, not a decision document.
- The user requests the linter to make the prose more persuasive rather than more honest.

## Failure modes

- **Over-pruning.** Stripping nuance to satisfy a rule. If the original carries meaning the rewrite does not, restore it.
- **Loss of voice.** Linting is not flattening. Preserve the author's tone where it does not violate a rule.
- **False precision.** Inventing numbers to satisfy "metric required". If no metric exists, mark it `[open question]`.
- **Cargo-culting the style.** Removing every adjective produces lifeless prose. The rules target *vague* adjectives, not all adjectives.

## Reviewer pass

After rewriting, run a second pass that checks:

- Every commitment has an owner *and* a date.
- Every comparative claim ("better", "faster", "more") has a baseline.
- Every "we believe" is either backed by evidence or relabeled `[assumption]`.

## Follow-up mechanism

- A linted PRFAQ feeds into `leadership-principles-reviewer`.
- A linted six-page narrative feeds into the decision meeting.
- Open Questions emitted by this skill should be assigned and tracked in the source document.

## Handoffs

**Consumes from**

- `working-backwards-prfaq`: `press_release` + FAQ prose → `draft`
- `six-page-narrative`: any section's prose → `draft`
- Any authoring skill that emits prose.

**Feeds into**

- `leadership-principles-reviewer`: linted prose → `proposal`
- The originating authoring skill: linted prose replaces the original section; Open Questions are assigned and tracked there.

Enums used: `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
