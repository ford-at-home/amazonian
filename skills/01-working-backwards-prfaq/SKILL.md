---
name: working-backwards-prfaq
description: Turn an idea into a PRFAQ (Amazon Working Backwards) packet — press release, customer FAQ, internal FAQ, MVP boundary, success metrics, risks, decision recommendation, and open questions. Use when defining a new product, feature, or internal initiative; when an idea needs sharpening before engineering or design starts; or when the user mentions PRFAQ, press release, working backwards, product definition, product brief, or product discovery.
---

# Working Backwards PRFAQ

Turn an unverified idea into a decision-ready PRFAQ packet. Refuses to proceed on vague customers, unmeasurable outcomes, or missing workarounds.

## Quick start

1. Collect the inputs below.
2. Run the validation gates *before* drafting. If any gate fails, stop and ask the user. Do not paper over.
3. Draft the PRFAQ using [`templates/prfaq-template.md`](templates/prfaq-template.md).
4. Run the validation gates a second time against the draft.
5. Emit the packet in the output schema below.

## When to use

- The user proposes a new product, feature, or internal tool.
- An existing idea needs sharpening before engineering or design starts.
- The user mentions: "PRFAQ", "press release", "working backwards", "product brief", "product definition", "product discovery".

## When NOT to use

- The decision is already made and the user wants execution help. Use `six-page-narrative` instead.
- The work is an operational fix or incident response. Use `correction-of-errors`.
- The artifact needed is a recurring process, not a one-time decision. Use `mechanism-designer`.

## Inputs

Gather these from the user. Do not synthesize them. If any are missing or hand-wavy, stop and ask.

```yaml
idea_name:                    # short product or feature name
customer:                     # specific role + context, not "users"
customer_problem:             # the problem the customer has today
current_workaround:           # what the customer does now
desired_customer_outcome:     # what becomes true after this exists
business_goal:                # why the company cares
constraints:                  # known limits (time, money, regulatory, technical)
known_evidence:               # facts, data, interviews, prior art
unknowns:                     # open questions the team has not answered
```

## Validation gates

Run these *before* writing the press release. A failing gate is a stop, not a soft warning.

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Vague customer | Customer is a named role with context (e.g. "platform engineer at a fintech with 50+ services"), not "developers" or "users" | Ask the user to narrow |
| Unlabeled assumptions | Every claim is tagged `[fact]`, `[assumption]`, `[inference]`, or `[open question]` | Re-tag and re-verify |
| Missing workaround | `current_workaround` is specific and observable, not "they suffer" | Ask: "What does the customer do today when this problem hits?" |
| Unmeasurable success | `desired_customer_outcome` has a metric, threshold, or observable behavior | Ask for the metric |
| No "why now?" | The packet explains what changed (cost, regulation, capability) that makes this the right moment | Ask the user |
| No out-of-scope | `mvp_boundary` lists at least three items explicitly *not* in scope | Add them |

## Process

1. **Collect** all inputs above. Use `[Unverified]` for anything the user could not confirm.
2. **Gate check #1** — run the validation gates. Stop if any fail.
3. **Draft** the press release. One page. Past tense. Customer-shaped, not feature-shaped.
4. **Draft** the Customer FAQ. 5–10 Q&A. Questions a real customer would ask on launch day.
5. **Draft** the Internal FAQ. 8–15 Q&A. Always include: "What did we consider and reject?", "What happens if we do nothing?", "Why now?", "What is the largest risk?"
6. **Fill** the remaining structured fields: MVP boundary, success metrics, risks, decision recommendation, open questions.
7. **Gate check #2** — re-run the validation gates against the draft. Strike or rewrite anything that fails.
8. **Emit** the packet in the output schema below.

## Output schema

```yaml
press_release:                # single-page, customer-shaped, past tense
customer_faq:                 # list of {question, answer}
internal_faq:                 # list of {question, answer}
mvp_boundary:
  in_scope:                   # list
  out_of_scope:               # list (at least 3 items)
success_metrics:              # list of {metric, baseline, target, measurement_method, time_to_evaluate}
risks:                        # list of {risk, severity, likelihood, mitigation, owner}
decision_recommendation:
  recommendation:             # one of: proceed | proceed_with_changes | do_not_proceed | needs_more_info
  rationale:                  # short paragraph; cites strongest evidence and largest risk
open_questions:               # list of {question, owner, due}
```

See [`templates/prfaq-template.md`](templates/prfaq-template.md) for the filled-in markdown form.

## Worked example

See [`examples/example-prfaq.md`](examples/example-prfaq.md) for a complete PRFAQ for a hypothetical product ("ChangeLens").

## Stop conditions

Stop and ask the user. Do not invent.

- Any input is missing or hedged ("users", "improve", "make better", "enhance").
- The proposed customer cannot articulate the workaround today.
- The success metric cannot be measured within 90 days of launch.
- The MVP boundary contains "and other things" or equivalent.

## Failure modes

- **Feature-shaped press release.** The headline describes the product, not the customer outcome. Rewrite from the customer's day.
- **Marketing-copy quotes.** Customer and leader quotes should sound like people, not brochures. Strip adjectives.
- **Internal FAQ that dodges hard questions.** Always include the rejected alternatives and the do-nothing case. If those are missing, the draft fails review.
- **Open questions as a hiding place.** A question answerable with one phone call should be answered before submission, not listed.
- **Success metric inflation.** "Customer delight" is not a metric. Demand a number.

## Reviewer pass

After the draft, run a second pass that checks:

- Every claim has an assumption tag.
- Every metric is measurable within 90 days.
- The largest risk is named and has a mitigation with an owner.
- The decision recommendation matches the evidence in the body. (A `proceed` recommendation with three high-severity unmitigated risks is incoherent.)

If `amazon-writing-linter` is available, hand the press release section to it before final emit.

## Follow-up mechanism

Once the PRFAQ is approved, the natural next artifacts are:

1. `mechanism-designer` — define the operating cadence that keeps this honest after launch.
2. `six-page-narrative` — if the proposal needs deeper architectural review.
3. `weekly-business-review` — wire the success metrics into a recurring inspection.

This skill emits a decision packet, not an execution plan. The PRFAQ is a contract; the work that follows is the implementation of that contract.

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
