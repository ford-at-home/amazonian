---
name: correction-of-errors
description: Run a blameless post-incident review (Correction of Errors / CoE) covering incident summary, customer impact, timeline, facts, Five Whys, root cause, detection and prevention gaps, action items, and follow-up. Refuses to stop at "human error" — asks why the system allowed the human action to create customer impact. Use after any production incident, customer-impacting outage, or process failure; or when the user mentions "CoE", "Correction of Errors", "postmortem", "post-incident review", "RCA", or "Five Whys".
category: constructive
required_reviews:
  - amazon-writing-linter
---

# Correction of Errors

Run a blameless post-incident review. The output is a structured document with a verified timeline, a Five Whys chain that does not stop at the human, named action items with owners, and a follow-up mechanism that ensures the actions actually land.

## Quick start

1. Collect the facts. Do not speculate yet.
2. Build the timeline from logs and human accounts.
3. Run the Five Whys. Do not stop at "human error".
4. Identify detection and prevention gaps separately.
5. Assign action items with owners and dates.
6. Schedule the follow-up that confirms the actions landed.

## When to use

- A customer-impacting incident occurred.
- A near-miss revealed a latent gap.
- A repeated incident indicates a pattern.
- The user mentions: "CoE", "Correction of Errors", "postmortem", "post-incident review", "RCA", "Five Whys", "blameless review".

## When NOT to use

- The incident is still active. Stabilize first; review after.
- The decision being made is forward-looking. Use `six-page-narrative` or `working-backwards-prfaq`.
- The artifact needed is a recurring mechanism, not a one-time review. Use `mechanism-designer`.

## Inputs

```yaml
incident_id:                  # internal identifier
incident_date:                # when it happened
incident_duration:            # start to mitigation
customer_impact:              # quantified: how many customers, what they experienced
detection_method:             # how the team learned about it (alert, customer report, etc.)
mitigation:                   # what was done to stop the bleeding
contributing_factors:         # raw list, unfiltered
logs_and_artifacts:           # links
human_accounts:               # what the responders observed and did
prior_incidents:              # similar past incidents, if any
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Blameless | No section names an individual as the cause. Roles and systems, not people | Rewrite |
| Customer impact quantified | A number: customers affected, requests failed, time lost, money lost | Add the number |
| Timeline complete | Detection → escalation → mitigation → resolution, with timestamps | Fill gaps |
| Five Whys reaches a system | The chain does not stop at "human error" or "X forgot" | Continue the chain |
| Detection and prevention separated | Gaps classified as "we could have caught this sooner" vs "we could have prevented this" | Re-classify |
| Action items have owner + date | Every action has both | Demand them |
| Follow-up scheduled | A specific date and owner for confirming actions landed | Add it |
| Required reviews completed | `amazon-writing-linter` has run against the timeline and root-cause prose and its revisions are incorporated | Run it; do not emit |

## Process

1. **Collect** facts from logs, monitoring, and human accounts. Tag each as `[fact]`, `[inference]`, or `[open question]`.
2. **Build the timeline** with timestamps. Distinguish what happened from what was noticed.
3. **Quantify customer impact**: customers affected, requests failed, time, money.
4. **Identify contributing factors** (multiple), not a single "the cause".
5. **Run the Five Whys** on each major contributing factor.
6. **Classify gaps** as detection vs prevention.
7. **Generate action items** that address gaps, not symptoms.
8. **Assign owners and due dates** to each action.
9. **Schedule the follow-up** that confirms the actions actually shipped.

## Non-negotiable rule

```text
Do not stop at "human error."
Ask why the system allowed the human action to create customer impact.
```

If a Five Whys chain ends with "person X did Y", continue: why was it possible for person X to do Y? Why did doing Y produce customer impact? Why was the impact not detected before it spread? The system always has more to say.

## Output schema

```markdown
# Correction of Errors — <incident_id>

## Incident Summary
<2–3 sentences. What happened, when, customer impact as a number.>

## Customer Impact
<Quantified: customers affected, requests/orders failed, time, money, trust signals.>

## Timeline
<Table: timestamp | event | source>

## Facts
<Tagged: [fact], [inference], [open question]. No speculation in this section.>

## Five Whys
<Chain per major contributing factor. Each chain ends at a system, not a person.>

## Root Cause
<The specific system condition that allowed this to happen. Not a person.>

## Detection Gap
<What was missing that would have surfaced this sooner.>

## Prevention Gap
<What was missing that would have prevented this entirely.>

## Action Items
<Owner, action, due date.>

## Owners and Due Dates
<Consolidated view.>

## Follow-Up Mechanism
<Date, owner. Confirms actions actually shipped.>
```

See [`coe-template.md`](coe-template.md). See [`examples/example-coe.md`](examples/example-coe.md) for a worked example.

## Stop conditions

- The incident is still ongoing.
- Facts are missing and the team is filling gaps with speculation.
- The team wants the document to assign blame.
- The proposed "root cause" is a person's name.

## Failure modes

- **Single-cause narrative.** Real incidents have multiple contributing factors. Beware the clean story.
- **Action item inflation.** Twenty action items is the same as zero — none will ship. Pick three to five with owners.
- **Action items that address symptoms.** "Add a Slack alert" when the gap is "the deployment process has no rollback". Address the gap.
- **Follow-up theater.** A follow-up that confirms the action items were "discussed" is not a follow-up. The follow-up confirms the actions shipped and the gap is closed.
- **Re-occurrence amnesia.** The same incident class recurs. Cross-reference prior CoEs.

## Follow-up mechanism

- Action items feed into `weekly-business-review` for tracking until closed.
- Recurring incidents of the same class feed into `mechanism-designer` for a structural fix.
- A pattern across multiple CoEs may feed into `working-backwards-prfaq` for a larger investment.

## Handoffs

**Consumes from**

- Operational facts (logs, monitoring, human accounts).
- `mechanism-designer`: when the failed artifact is a mechanism, the mechanism spec → `contributing_factors`
- `weekly-business-review`: persistent variance on a metric → `prior_incidents` / `contributing_factors`

**Feeds into**

- `weekly-business-review`: `action_items` → next week's `action_items` (tracked until closed)
- `mechanism-designer`: structural gaps → `goal` + `failure_mode_today` for a new mechanism
- `working-backwards-prfaq`: pattern across multiple CoEs → new PRFAQ for a larger investment
- `dissent-before-commit`: recent incidents on adjacent systems → `state_changes_since_authoring` (used by DBC to re-canvass dissent against current state)

Enums used: `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml). See [`GLOSSARY.md`](../../GLOSSARY.md#blameless) for the definition of "blameless" used here.

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
