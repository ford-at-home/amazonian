# Example: Navigator output on the ChangeLens manifest

This walks through what `14-lifecycle-navigator` produces given the worked example manifest at [`skills/00-repo-state-import/examples/example-bootstrap.yaml`](../../00-repo-state-import/examples/example-bootstrap.yaml).

## Inputs

```yaml
manifest_path: /repo/governance.yaml      # the ChangeLens example bootstrap
operator_handle: w.prior
session_intent: null
prefer_superpowers_override: null
```

## Step 1 — Validate

```text
Schema validation: PASS (governance.yaml conforms to schema v1)
```

## Step 2 — Compute chain state

The navigator walks `state-machine.yaml` positions in order:

- `pre-bootstrap`: `bet.bootstrapped_at` is `"2026-05-21T20:30:00Z"` → precondition `empty(bet.bootstrapped_at)` is **false**. Skip.
- `pre-discovery`: `bet.prfaq_path` is `"docs/prfaq.md"` → precondition `empty(bet.prfaq_path)` is **false**. Skip.
- `discovery-complete`: `bet.prfaq_path` is populated → precondition `empty(bet.prfaq_path)` is **false**. Skip.
- `prfaq-incomplete`: PRFAQ exists, `count(success_metrics, ==, 0)` is **false** (2 metrics). Skip.
- `design-pending`: PRFAQ exists, metrics ≥ 1, `count(live_mechanisms, ==, 0)` is **false** (2 mechanisms). Skip.
- `pre-launch`: mechanisms ≥ 1 — preconditions could match, but `last_launch_readiness_review` is not a v1 manifest field; the position is skipped as `[Unverified]` per the state-machine note.
- `operating-wbr-due`: `cadence_due(live_mechanisms[wbr])` — evaluated against the absence of any recent WBR run in `history[]`. **Matches.**
- (later positions not evaluated; first match wins)

**Selected position:** `operating-wbr-due`
**Recommended skill:** `05-weekly-business-review`
**Upstream fields:** `[live_mechanisms, success_metrics]`

## Step 3 — Phase-laundering second-axis check

Trace each upstream field's evidence tag in the manifest:

| Field | Evidence tag | Source |
|---|---|---|
| `live_mechanisms[wbr-monday]` | `assumption` | inferred from calendar invite; no spec |
| `live_mechanisms[incident-retro]` | `fact` | `docs/retro-template.md` |
| `success_metrics[time-to-status]` | `fact` | dashboard URL |
| `success_metrics[confirmation-throughput]` | `fact` | dashboard URL |

**Finding:** `live_mechanisms[wbr-monday]` is tagged `assumption`. The WBR's *mechanism* is inferred, not contracted. Running `05-weekly-business-review` against an `assumption`-tagged mechanism would stress-test laundered design — the canonical `phase laundering` shape.

**Demotion:** `routing_decision: advance` → `routing_decision: upstream_remediation`.

**Producing skill** (from `producing_skill_map`): `live_mechanisms` → `04-mechanism-designer`.

## Step 4 — Select questioning mode

`config.prefer_superpowers: auto` (from manifest). Probe for `superpowers:brainstorming`.

Result: `[Unverified] superpowers detection inconclusive on this platform`. Fall back to native loop.

## Step 5 — Run native questioning loop

The navigator prepares inputs for `04-mechanism-designer`:

```yaml
inputs_prepared:
  goal:
    statement: "Reduce P95 customer-reported time-to-status from 47 minutes to 30 minutes"
    source: governance.yaml.period_goals[2026-Q2].goals[g1]
    evidence: fact
  existing_mechanism:
    name: "Monday Weekly Business Review"
    cadence: weekly
    written_spec: false
    evidence: assumption                # the key finding — there is no spec
  success_metrics:
    - id: time-to-status
      target: 30
      current: 47
      unit: minutes
      type: output_metric
    - id: confirmation-throughput
      target: 60
      current: 42
      unit: confirmations_per_hour
      type: input_metric
  remediation_intent: |
    Convert the implicit Monday WBR into a designed mechanism with cadence,
    inputs, inspection method, escalation rule, and a 30-day trial.
    Then 05-weekly-business-review can run against a contracted mechanism
    rather than laundered design.
```

The questioning loop confirms the operator wants to proceed with mechanism design rather than just running WBR against the implicit cadence (which would be `phase laundering`).

## Step 6 — Append history entry

```yaml
- timestamp: "2026-05-21T21:00:00Z"
  invoked_by: w.prior
  state_snapshot_hash: "9c2f8a1"
  recommended_skill: 04-mechanism-designer
  rationale: |
    Position operating-wbr-due selected based on cadence_due check. However,
    phase-laundering second-axis check found that live_mechanisms[wbr-monday]
    is evidence: assumption (inferred from calendar invite; no written spec).
    Routing demoted from advance to upstream_remediation. Producing skill for
    live_mechanisms is 04-mechanism-designer. Recommend designing the WBR as
    a proper mechanism before invoking 05-weekly-business-review against it.
  inputs_provided:
    goal_statement: "Reduce P95 customer-reported time-to-status to 30 minutes"
    existing_mechanism_name: "Monday Weekly Business Review"
    has_written_spec: false
    target_skill: 04-mechanism-designer
  handoff_status: proposed
  routing_decision: upstream_remediation
```

## Step 7 — Hand off

Operator console:

```text
Next: 04-mechanism-designer
Routing decision: upstream_remediation
Why: The position operating-wbr-due matched on cadence, but the second-axis
     phase-laundering check found live_mechanisms[wbr-monday] is tagged
     evidence: assumption — the Monday WBR has no written spec. Running
     05-weekly-business-review against an assumption-tagged mechanism
     would stress-test laundered design. Producing skill for that field
     is 04-mechanism-designer.

Inputs prepared:
  goal_statement: "Reduce P95 customer-reported time-to-status to 30 minutes"
  existing_mechanism_name: "Monday Weekly Business Review"
  has_written_spec: false
  success_metrics: [time-to-status (47 → 30 min), confirmation-throughput (42 → 60/hr)]

Run 04-mechanism-designer now? (y / n / explain why this routing)
```

## What this example shows

1. The navigator does not blindly recommend the most obvious next skill (`05-weekly-business-review` here) — it traces upstream evidence first.
2. `assumption`-tagged manifest fields are a routing signal, not a blocker. The route is to the *producing* skill of the laundered field, not to a hard stop.
3. `history[]` records both the original position selection *and* the demotion, with the full rationale. The audit trail makes the navigator's decision inspectable.
4. The `[Unverified]` superpowers detection is surfaced honestly; the operator can resolve it with a one-line config change.

This is what *phase laundering being refused* looks like in practice: the surface signal said "WBR is due" and the navigator said "first, contract the mechanism that the WBR will inspect."
