---
name: leadership-principles-reviewer
description: Evaluate a proposal, project, PRFAQ, or six-page narrative against Amazon-style leadership principles. Surfaces strongest and weakest alignment, contradictions, missing evidence, and risks hidden by optimism. Use when reviewing a PRFAQ before submission, when stress-testing a strategy doc, when a proposal feels "too clean", or when the user mentions "LP review", "leadership principles", "stress test", "red team", or "pre-mortem".
---

# Leadership Principles Reviewer

Read a proposal and evaluate it against the leadership principles in [`rubric.yaml`](rubric.yaml). The output is structured, opinionated, and explicit about what is missing — including the risks the proposal hides behind optimism.

This skill is a reviewer, not an author. It does not rewrite the proposal; it surfaces what the author should re-examine.

> Note: the Amazon Leadership Principles are property of Amazon.com, Inc. The rubric used here is an independent interpretation of publicly described principles for the purpose of evaluating written artifacts; it is not Amazon's official rubric and is not endorsed by Amazon.

## Quick start

1. Read the proposal end-to-end.
2. Score each principle in [`rubric.yaml`](rubric.yaml) as strong / weak / silent / contradictory.
3. List the strongest and weakest alignments.
4. Flag contradictions between principles (e.g., "Bias for Action" used to justify skipping "Are Right, A Lot").
5. List missing evidence and risks hidden by optimism.
6. Emit recommended revisions.

## When to use

- A PRFAQ or six-page narrative is drafted and ready for review.
- A proposal feels "too clean" and needs adversarial reading.
- The user mentions: "LP review", "leadership principles", "stress test", "red team", "pre-mortem", "adversarial review".

## When NOT to use

- The proposal does not yet exist. Use `working-backwards-prfaq` or `six-page-narrative` to draft first.
- The artifact is a post-incident review. Use `correction-of-errors`; its blamelessness rules differ from this reviewer's stance.
- The goal is to make the proposal more persuasive. This skill makes the proposal more *honest*, which is sometimes the opposite.

## Inputs

```yaml
proposal:                     # the drafted artifact (PRFAQ, six-pager, memo)
proposal_type:                # prfaq | six_pager | memo | other
known_context:                # context the reviewer should know but which is not in the doc
known_dissent:                # any dissent already surfaced
```

## Principles

The full rubric — with what each principle means *for the purpose of evaluating a written artifact* and what evidence to look for — lives in [`rubric.yaml`](rubric.yaml).

Summary list:

- customer_obsession
- ownership
- invent_and_simplify
- are_right_a_lot
- learn_and_be_curious
- insist_on_highest_standards
- think_big
- bias_for_action
- frugality
- earn_trust
- dive_deep
- have_backbone_disagree_and_commit
- deliver_results

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Every principle scored | strong / weak / silent / contradictory | Score the unscored |
| At least one weakness | If everything is strong, the review is incomplete | Re-read |
| Contradictions surfaced | Cases where one principle is invoked to skip another | List them |
| Missing evidence listed | Specific claims that need evidence the doc does not provide | List them |
| Risks hidden by optimism | At least one risk understated or omitted | Name them |
| Recommended revisions | Specific, owner-able, ≤ 5 | Trim or expand |

## Process

1. **Read** the proposal end-to-end before scoring any principle.
2. **Score** each principle. Use evidence from the doc; cite passages where possible.
3. **Identify** the two strongest and two weakest alignments.
4. **Hunt for contradictions**. Bias-for-action used to skip dive-deep is a common one.
5. **List missing evidence**. Where does the proposal assert something the reviewer cannot verify?
6. **List risks hidden by optimism**. What is the worst-case outcome the proposal does not address?
7. **Emit** the output schema below.

## Output schema

```markdown
# Leadership Principles Review — <proposal title>

## Strongest Alignment
<2–3 principles with citations from the proposal.>

## Weakest Alignment
<2–3 principles with citations and what is missing.>

## Contradictions
<Cases where one principle is invoked to skip another. Cite both sides.>

## Missing Evidence
<Specific claims the proposal asserts that the reviewer cannot verify, with what evidence would resolve each.>

## Risks Hidden By Optimism
<Worst-case outcomes the proposal understates or omits.>

## Recommended Revisions
<≤ 5 specific, owner-able changes the author should make before submission.>
```

## Stop conditions

- The proposal is shorter than two pages — too little surface area to review against 13 principles.
- The proposal has no decision in it (it is a status update). Send to a different reviewer.
- The user requests the reviewer to confirm the proposal is good. This skill does not provide reassurance.

## Failure modes

- **Sycophantic review.** Everything scored "strong". Re-read; if nothing is weak, the reviewer is failing.
- **Principle bingo.** Mechanically applying all 13 principles when only 4–6 are load-bearing for this proposal. Focus on the load-bearing ones.
- **Vague critique.** "This could be stronger." Cite passages and propose specific revisions.
- **Rubric absolutism.** Treating one independent interpretation of the principles as the only valid lens. It is one lens; treat it accordingly.

## Follow-up mechanism

- Revisions feed back into `working-backwards-prfaq` or `six-page-narrative`.
- If multiple proposals show the same weakness pattern, the pattern itself may feed into `mechanism-designer` for a structural improvement.

## Handoffs

**Consumes from**

- `working-backwards-prfaq`: full packet → `proposal` (`proposal_type: prfaq`)
- `six-page-narrative`: full memo → `proposal` (`proposal_type: six_pager`)
- `amazon-writing-linter`: linted draft → `proposal` (prefer linting first when available)

**Feeds into**

- `working-backwards-prfaq`: `recommended_revisions` → author updates the PRFAQ
- `six-page-narrative`: `recommended_revisions` → author updates the memo
- `mechanism-designer`: cross-proposal weakness patterns → `goal` + `failure_mode_today`

Enums used: `principle_scores`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
