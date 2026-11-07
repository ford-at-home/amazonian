# Mechanism — <name>

> Conforms to `mechanism-designer`. Every section is required.

---

## Goal

<One sentence. The outcome this mechanism keeps producing.>

## Operating Cadence

- **Interval:** <daily | weekly | monthly | event-driven>
- **Day / time (if scheduled):** <e.g., "Tuesdays 10:00 ET">
- **Trigger (if event-driven):** <the specific event>

## Inputs

| Input | Source | Owner of source | Format |
|-------|--------|------------------|--------|
|       |        |                  |        |

## Process

1. <Step>
2. <Step>
3. <Step>

> Each step has an actor (who does it) and an artifact (what they produce or read).

## Outputs

| Output | Audience | Storage location | Retention |
|--------|----------|------------------|-----------|
|        |          |                  |           |

## Inspection Method

- **Inspector:** <named individual, not the owner>
- **Inspection cadence:** <e.g., monthly>
- **Inspection artifact:** <what the inspector produces>

## Escalation Rule

- **If:** <specific condition, e.g., "the mechanism is skipped twice in a row">
- **Then:** <specific action, e.g., "the inspector notifies the VP within 24 hours">
- **Owner of escalation:** <named individual>

## Failure Modes

- <How this mechanism could silently fail and still appear healthy>
- <…>

## Anti-Patterns

- <Behaviors that signal decay, e.g., "the agenda becomes purely informational">
- <…>

## First 30-Day Trial

- **Start date:** <YYYY-MM-DD>
- **Pass criteria:** <measurable>
- **Fail criteria:** <measurable>
- **Review date:** <YYYY-MM-DD>
- **Reviewer:** <named individual>

> Outcomes of the 30-day review: keep, revise, or retire. All three are valid; "ignore" is not.
