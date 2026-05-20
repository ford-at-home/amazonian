# Correction of Errors — <incident_id>

> Blameless post-incident review. No individuals named as cause. Five Whys must reach a system, not a person.
> Tag every claim: `[fact]`, `[inference]`, `[open question]`.

---

## Incident Summary

<2–3 sentences. What happened, when, customer impact as a number.>

- **Incident ID:** <ID>
- **Date:** <YYYY-MM-DD>
- **Duration:** <start to mitigation>
- **Severity:** <SEV-1 / 2 / 3>

## Customer Impact

- **Customers affected:** <number>
- **Requests / orders / sessions impacted:** <number>
- **Money:** <if measurable>
- **Trust signals:** <support tickets, social, churn intent>

## Timeline

| Timestamp (UTC) | Event | Source |
|------------------|-------|--------|
|                  | Symptom first present (often before detection) | logs |
|                  | First alert / first customer report | <source> |
|                  | Responder engaged | <source> |
|                  | Mitigation applied | <source> |
|                  | Customer impact ended | <source> |
|                  | Incident closed | <source> |

> Distinguish "what happened" from "what was noticed". Detection delay is a separate gap.

## Facts

- `[fact]` <verifiable statement with source>
- `[inference]` <statement derived from facts>
- `[open question]` <question to resolve before closing the CoE>

## Five Whys

### Contributing factor A: <name>

1. Why did <event> happen? <answer>
2. Why <answer 1>? <answer>
3. Why <answer 2>? <answer>
4. Why <answer 3>? <answer>
5. Why <answer 4>? <answer — must reach a system condition, not a person>

### Contributing factor B: <name>

<same chain>

## Root Cause

<The specific system condition. Not a person. Not "we should be more careful".>

## Detection Gap

<What was missing that would have surfaced this sooner. Examples: missing alert, alert threshold too loose, no synthetic check on the customer flow, no on-call rotation for this surface.>

## Prevention Gap

<What was missing that would have prevented this entirely. Examples: no canary deploy, no integration test for the edge case, no rate limit, no schema validation, no rollback path.>

## Action Items

| # | Action | Type (detection / prevention / process) | Owner | Due |
|---|--------|-----------------------------------------|-------|-----|
| 1 |        |                                         |       |     |

> Three to five action items is the right number. Twenty is zero.

## Owners and Due Dates (consolidated)

| Owner | Action items |
|-------|--------------|
|       |              |

## Follow-Up Mechanism

- **Follow-up date:** <YYYY-MM-DD>
- **Owner:** <named individual>
- **Confirms:** <each action shipped, gap closed, no re-occurrence>

> The follow-up confirms the actions shipped, not that they were discussed.

## Prior incidents of this class

| Incident ID | Date | Same root cause? |
|-------------|------|-------------------|
|             |      |                   |
