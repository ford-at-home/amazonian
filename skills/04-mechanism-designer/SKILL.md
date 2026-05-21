---
name: mechanism-designer
description: Convert a goal into a recurring operational mechanism with cadence, inputs, outputs, inspection method, escalation rule, and a 30-day trial. Use when a one-off effort needs to become recurring practice, when "we will try harder" is the current plan, when a goal has been set but has no operating cadence, or when the user mentions "mechanism", "process", "cadence", or "operationalize".
category: constructive
required_reviews:
  - amazon-writing-linter
---

# Mechanism Designer

Convert a goal into a mechanism that produces the desired behavior after motivation runs out. Goals without mechanisms decay; mechanisms with bad design also decay, but visibly. The point of this skill is to make decay visible.

## Quick start

1. Collect the inputs below.
2. Identify the failure mode today — the specific way the goal does not happen now.
3. Specify cadence, inputs, outputs, inspection, and escalation.
4. Use [`mechanism-template.md`](mechanism-template.md) for the prose form.
5. Define a 30-day trial with explicit pass/fail criteria.

## When to use

- A goal has been set but no recurring practice supports it.
- A one-off effort needs to become recurring practice.
- The current plan is "we will try harder" or "we will be more disciplined".
- A metric has been defined but no one is inspecting it on cadence.
- The user mentions: "mechanism", "process", "operationalize", "cadence".

## When NOT to use

- The decision has not been made yet. Use `working-backwards-prfaq` or `six-page-narrative` first.
- The mechanism failed and the question is "why?" — use `correction-of-errors`.
- The cadence already exists and just needs running. This skill designs cadences; it does not run them.

## Inputs

```yaml
goal:                         # the outcome we want to keep producing
failure_mode_today:           # the specific way it does not happen now
desired_behavior:             # what people or systems do under the mechanism
cadence:                      # daily | weekly | monthly | event-driven
owner:                        # a named individual, not a team
inputs:                       # data or artifacts the mechanism consumes
outputs:                      # artifacts the mechanism produces
inspection_method:            # how someone confirms it is working
escalation_path:              # who is notified, when, and what they do
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Named owner | A specific person, not a team or role | Ask who specifically |
| Specific cadence | A defined interval or trigger, not "regularly" | Demand a number or trigger |
| Observable output | The mechanism produces a tangible artifact each run | Define one |
| Inspection method | Someone other than the owner inspects it | Name the inspector |
| Escalation rule | Explicit "if X, then notify Y within Z" | Write it |
| Mechanism failure mode named | The author can name how the mechanism will silently fail | Demand the answer |
| Required reviews completed | `amazon-writing-linter` has run against the mechanism spec and its revisions are incorporated | Run it; do not emit |

## Process

1. **State** the goal in customer or system terms.
2. **Diagnose** the current failure mode. Be specific: what does the system do today that prevents the goal?
3. **Design** the mechanism using [`mechanism-template.md`](mechanism-template.md).
4. **Specify** the inspection method. The owner should not be the sole inspector.
5. **Specify** the escalation rule. Without this, silent failure is the default.
6. **Pre-mortem** the mechanism. Name how it will go wrong.
7. **Trial** for 30 days with explicit pass/fail criteria.

## Output schema

```yaml
mechanism:
  goal:
  operating_cadence:          # interval and/or trigger
  inputs:
  process_steps:              # ordered
  outputs:
  inspection_method:          # who, what, when
  escalation_rule:            # if X, notify Y within Z
  failure_modes:              # how this mechanism will silently fail
  anti_patterns:              # behaviors that signal decay
  thirty_day_trial:
    start_date:
    pass_criteria:            # measurable
    fail_criteria:            # measurable
    review_date:
    reviewer:
```

See [`mechanism-template.md`](mechanism-template.md) for the prose form.

## Stop conditions

- "Owner" is a team name, a role, or a rotating list with no named individual.
- "Cadence" is "as needed", "regularly", or "ongoing".
- The inspection is performed only by the owner.
- The escalation rule is "we will discuss it".

## Failure modes

- **Owner without authority.** Naming someone who cannot actually enforce the mechanism. Either change the owner or change the mechanism.
- **Inspection by the same person.** Owners marking their own homework. The inspector must be a second party.
- **Cadence drift.** A weekly mechanism becomes "every other week", then "when we remember". The escalation rule must fire on missed cadences.
- **Mechanism that protects the author.** A mechanism that always produces "everything is fine" is broken.
- **Theater.** A meeting with no inputs or outputs is not a mechanism. It is a meeting.

## Follow-up mechanism

- Recurring inspections often become `weekly-business-review` inputs.
- When the mechanism fails, run `correction-of-errors` on the mechanism itself, not just on the underlying incident.
- After 30 days, the trial review either confirms the mechanism (keep), revises it (modify), or kills it (retire). All three are valid outcomes; "ignore the trial" is not.

## Handoffs

**Consumes from**

- `working-backwards-prfaq`: `success_metrics` → `inputs` (the metrics the mechanism inspects); one `success_metrics[].metric` → `goal`
- `six-page-narrative`: "Proposed Mechanism" section → `desired_behavior`; "Metrics" → `inputs`

**Feeds into**

- `weekly-business-review`: `mechanism.inspection_method` defines the WBR's structure; `mechanism.outputs` + `mechanism.inputs` → `input_metrics` / `output_metrics`
- `correction-of-errors`: when the mechanism itself fails, the mechanism spec is the artifact under review → `contributing_factors`
- `launch-readiness-review`: operational gaps the launch needs to close → review consumes the mechanism's `inspection_method` to verify metric instrumentation is wired before ship
- `tenets-review`: when the bet's operating mechanism is the artifact being reviewed → `mechanism.outputs` → `metrics_snapshot`

Enums used: `metric_types`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
