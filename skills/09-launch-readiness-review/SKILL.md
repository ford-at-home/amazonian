---
name: launch-readiness-review
description: Gate the launch of a feature, product, or initiative by diffing the current build state against the original PRFAQ contract. Emits one of go / no_go / conditional_go / defer with a PRFAQ drift report, predicted failure modes (pre-mortem), risk register delta, and rollback testability check. The named failure mode is PRFAQ drift — the gap between authoring-time promise and ship-time reality, where the surface signal (features shipped match the PRFAQ scope) hides that the customer outcome the PRFAQ promised is not being delivered. Use when an artifact authorized by a PRFAQ or six-page narrative is approaching launch; or when the user mentions "launch readiness", "go/no-go", "ship review", "pre-launch review", or "launch gate".
category: interrogative
---

# Launch Readiness Review

Gate a launch by diffing the build against the PRFAQ contract. The PRFAQ promised something; the build is something. This skill names the gap and decides whether the gap is small enough to ship through.

This skill is interrogative. Its job is to fail launches that should fail. A reviewer asked to "confirm this is ready" is being asked to fail at its job — and will refuse.

## Quick start

1. Collect the inputs below. The PRFAQ that authorized the work is required.
2. Reconnect the build to the customer outcome the PRFAQ promised — not just to the scope artifact.
3. Run the validation gates. A failed gate forces `no_go` or `defer`; it does not soften to `conditional_go`.
4. Generate the pre-mortem: predicted failure modes derived from the risk register delta.
5. Emit the gate decision with the launch narrative attached *only* if the decision is `go`.

## When to use

- A feature or product authorized by a PRFAQ is approaching ship date.
- A team is asking for go/no-go sign-off.
- A previous launch over-promised; this skill exists to prevent the next one.
- The user mentions: "launch readiness", "go/no-go", "ship review", "pre-launch", "launch gate", "ship checklist".

## When NOT to use

- No PRFAQ exists. Without the contract, there is nothing to diff against. Send the team back to `working-backwards-prfaq` or refuse.
- The artifact has already shipped. Use `weekly-business-review` to inspect post-launch metrics or `correction-of-errors` if something broke.
- The user wants a launch-comms plan or rollout schedule. This skill gates the ship decision; it does not plan the rollout.

## Inputs

```yaml
original_prfaq:                 # the PRFAQ packet that authorized this work; required
current_build_state:
  features_shipped:             # mapped to PRFAQ `mvp_boundary.in_scope` items, item-by-item
  features_deferred:            # items originally promised but not built
  known_defects:                # list of {defect, severity, customer_impact}
  performance_benchmarks:       # measured against any PRFAQ-promised thresholds
customer_outcome_evidence:      # REQUIRED — evidence the build produces the PRFAQ's `desired_customer_outcome`
                                # at minimum: dogfood data, beta cohort behavior, or a documented synthetic test
success_metrics_status:
  - metric:                     # from PRFAQ success_metrics
    target:
    instrumentation_status:     # not_built | built_untested | validated
    baseline_measured:          # bool
launch_scope:
  audience:                     # quantified: % traffic, named cohort, internal-only, etc.
  support_readiness:            # who handles inbound; runbook exists?
rollback_testing:               # REQUIRED — rollback existence is not rollback testability
  mechanism:                    # feature_flag | deploy_revert | data_rollback | none
  tested:                       # bool — has the rollback actually been exercised?
  propagation_time:             # how long until rollback takes effect end-to-end
  owner_on_call:                # named individual responsible for triggering rollback
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Customer outcome reconnected | `customer_outcome_evidence` cites at least one piece of evidence the build produces the PRFAQ's `desired_customer_outcome` | `no_go` — the build may ship features but not the promised outcome |
| Metric instrumentation validated | Every `success_metrics_status[].instrumentation_status == validated`, with `baseline_measured == true` | `no_go` for any `built_untested`; `defer` if `not_built` |
| Rollback tested, not just planned | `rollback_testing.tested == true` AND `propagation_time` is documented AND `owner_on_call` is a named individual | `defer` until the rollback is exercised |
| No blocking drift | No `prfaq_drift[].severity == blocking` | `no_go` |
| Conditions are themselves gated | Every entry in `conditions` has its own `owner` and `gate_date`; nothing post-launch | Strip post-launch conditions; reassess as `go-with-risk` documented in launch narrative |
| Pre-mortem generated | `predicted_failure_modes` is non-empty and each entry has a leading indicator and a response owner | Generate it; do not skip |

## Process

1. **Read the PRFAQ.** Extract `desired_customer_outcome`, `success_metrics`, `mvp_boundary`, and `risks`. These are the contract.
2. **Diff features.** For each `mvp_boundary.in_scope` item, locate it in `current_build_state.features_shipped` or `features_deferred`. Rate each drift per [`GLOSSARY.md`](../../GLOSSARY.md#prfaq-drift-severity).
3. **Reconnect to the customer.** Do not advance past this step until `customer_outcome_evidence` answers: *does what is about to ship produce the customer outcome the PRFAQ promised?* A scope match alone does not.
4. **Check metric instrumentation.** Any `built_untested` is a `no_go` candidate. Any `not_built` forces `defer`.
5. **Probe rollback testability.** "We can revert the commit" is not a rollback plan. Require evidence the rollback has been exercised.
6. **Delta the risk register.** For each PRFAQ risk, classify current status per [`GLOSSARY.md`](../../GLOSSARY.md#risk-status). Risks that `materialized` are inputs to the pre-mortem.
7. **Generate the pre-mortem.** For each material drift, materialized risk, or unproven mitigation, write a `predicted_failure_mode` with a leading indicator and a response owner.
8. **Decide.** Apply the gates. The decision is the most conservative outcome any gate forces; gates do not vote.
9. **Emit launch narrative only on `go`.** A `no_go` with a confident narrative is a contradiction.

## Hard rule (non-negotiable)

```text
A scope match is not a customer-outcome match.
A planned rollback is not a tested rollback.
A condition that fixes post-launch is not a condition — it is risk.
A launch narrative on a no_go is a contradiction; do not emit it.
```

## Output schema

```yaml
gate_decision:                  # go | no_go | conditional_go | defer
gate_rationale:                 # the most conservative gate that forced this decision, cited
conditions:                     # only if conditional_go; each MUST gate before ship
  - condition:
    owner:                      # named individual
    gate_date:                  # before ship date
    blocking_until_met:         # bool — true required for conditional_go
prfaq_drift:
  - original_commitment:        # cited from PRFAQ
    current_reality:
    severity:                   # blocking | significant | acceptable
customer_outcome_assessment:    # REQUIRED
  promised_outcome:             # cited from PRFAQ desired_customer_outcome
  evidence_of_delivery:         # from customer_outcome_evidence
  confidence:                   # [fact] | [assumption] | [inference] | [open question]
metric_instrumentation_gaps:    # any not_built or built_untested metrics
risk_register_delta:
  - risk:                       # from PRFAQ risks
    original_mitigation:
    current_status:             # mitigated | open | materialized
    if_materialized:            # outcome and what we learned
predicted_failure_modes:        # the pre-mortem
  - failure_mode:               # what could go wrong post-launch
    leading_indicator:          # what we'd see if it's happening (must be measurable)
    response:                   # what we do when we see it
    owner:                      # named individual who watches
rollback_assessment:
  mechanism:
  tested:
  propagation_time:
  owner_on_call:
  acceptable:                   # bool — derived
launch_narrative:               # 2-3 sentences leadership can use in the WBR
                                # ONLY emitted if gate_decision == go
                                # null otherwise — do not soften no_go
```

## Stop conditions

- No PRFAQ exists. Refuse; route the team to `working-backwards-prfaq`.
- The team requests confirmation that the launch is ready. Refuse; offer to surface blocking drift instead.
- `customer_outcome_evidence` is missing entirely. The customer is the point; without evidence of customer-outcome delivery, the gate cannot run.
- The launch has already shipped. This is a `correction-of-errors` situation, not a readiness review.

## Failure modes

### Named failure mode (the one this skill exists to catch)

- **PRFAQ drift.** The gap between what the PRFAQ promised at authoring time and what the build actually delivers at launch time. The surface signal — features shipped match the PRFAQ scope, the team is on the original timeline — hides that the planned features do not produce the promised customer outcome, or that scope crept silently, or that the risk register's mitigations have decayed. The skill's second-axis check is the `customer_outcome_assessment` gate: a scope match is not a customer-outcome match. See [`GLOSSARY.md#prfaq-drift`](../../GLOSSARY.md#prfaq-drift) for the cross-reference index. Specific sub-patterns of this failure mode — scope-match satisficing, narrative laundering, PRFAQ-as-stale-artifact rationalization — appear below.

### Other failure modes

- **Scope-match satisficing.** Confirming features_shipped against mvp_boundary.in_scope and stopping there. The customer-outcome gate exists to prevent this. (The canonical instance of PRFAQ drift.)
- **Soft conditional_go.** Conditions like "we'll add monitoring next sprint" make the decision `go-with-risk`. Reject them as conditions; document them as accepted risk in the launch narrative or refuse to ship.
- **Pre-mortem theater.** Generating predicted_failure_modes without leading indicators or owners. A failure mode no one is watching for is a failure mode that lands silently.
- **Rollback hand-waving.** "We have feature flags" without evidence the rollback has been exercised. Untested rollback in production is the same as no rollback.
- **Narrative laundering.** Writing a launch narrative that obscures `significant` drift. The narrative must surface drift; it does not erase it. (A specific instance of PRFAQ drift.)
- **PRFAQ-as-stale-artifact rationalization.** "The PRFAQ is six months old, requirements have changed." If the contract changed, the contract should be re-signed (re-run the PRFAQ skill), not silently ignored. (A specific instance of PRFAQ drift.)

## Reviewer pass

After emitting, run a second pass that checks:

- The `gate_decision` is the most conservative outcome any gate forced — not an average.
- `launch_narrative` is null if `gate_decision != go`.
- Every `predicted_failure_mode` has a leading indicator that someone is actually watching.
- `conditional_go` (if used) has no post-launch conditions.
- `customer_outcome_assessment.confidence` is honest — `[fact]` requires measured evidence, not a deck slide.

## Follow-up mechanism

- `gate_decision: go` → the artifact ships; predicted_failure_modes become inputs to the first WBR cycle.
- `gate_decision: no_go` → the team addresses blocking drift and re-runs the review.
- `gate_decision: conditional_go` → conditions are tracked to their gate_dates; a follow-up review confirms they were met before ship.
- `gate_decision: defer` → revisit on a specific date the team commits to; no defer without that date.
- All `predicted_failure_modes` are archived; if any materialize, they become inputs to a `correction-of-errors`.

## Handoffs

**Consumes from**

- `working-backwards-prfaq`: full packet → `original_prfaq`; `success_metrics` → `success_metrics_status`; `risks` → `risk_register_delta`; `mvp_boundary.in_scope` → drift basis; `desired_customer_outcome` → `customer_outcome_assessment`
- `six-page-narrative` (when applicable): "Proposed Mechanism" section + "Metrics" → contract basis
- Engineering systems: feature lists, defect lists, benchmark results → `current_build_state`

**Feeds into**

- `weekly-business-review`: `predicted_failure_modes` → first-week `risks` / `issues`; `metric_instrumentation_gaps` → `action_items`
- `correction-of-errors`: if a `predicted_failure_mode` materializes post-launch, this output is `prior_incidents` context
- `working-backwards-prfaq`: blocking drift → revisions to the next PRFAQ (the contract was wrong, not just the build)
- `mechanism-designer`: if launch reveals operational gaps not in the PRFAQ, those become new mechanism inputs
- `dissent-before-commit`: `predicted_failure_modes` → `dissent_history` (when a `go` or `conditional_go` is queued for execution, DBC re-canvasses against current state)

Enums used: `gate_decisions`, `prfaq_drift_severity`, `risk_status`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
