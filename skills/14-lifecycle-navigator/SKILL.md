---
name: lifecycle-navigator
description: Read governance.yaml, identify the next required Amazonian skill given the bet's current state, and route the operator either through superpowers:brainstorming (when present) or a minimal native questioning loop (when not). The named failure mode is phase laundering — recommending an advanced-phase interrogative skill against manifest fields that are themselves assumption-tagged from bootstrap, so the recommended stress test runs on laundered state. Refuses confirmatory invocation. Use at session start once governance.yaml exists, when the operator asks "what should I do next", or when they mention "lifecycle navigator", "next step", "what's next", "where am I in the chain", "PDLC flow", or "manage me through the suite".
category: interrogative
---

# Lifecycle Navigator

Read [`governance.yaml`](../../scripts/templates/governance-template.yaml). Compute where this bet sits in the PDLC chain. Recommend the next required Amazonian skill — or, when an upstream gap is detected, route the operator to the *producing* skill of the missing field instead of the *consuming* skill that would have stress-tested its laundered version.

This skill is interrogative. It produces a routing recommendation and appends an entry to `governance.yaml.history[]`. It does not author bet artifacts. If asked to "confirm we're ready for launch" or "tell me everything's fine," it refuses — that posture is exactly the surface signal `phase laundering` hides behind. See [`phase laundering`](../../GLOSSARY.md#phase-laundering).

## Quick start

1. Validate `governance.yaml` against [`schema/governance.schema.json`](../../schema/governance.schema.json). Surface schema errors and stop if invalid.
2. Compute the **chain state** by mapping populated manifest fields to the chain positions documented in [`state-machine.yaml`](state-machine.yaml).
3. Identify the next required skill — or, if any upstream gate would be against an `assumption`/`open_question`-tagged field, identify the *producing* skill for that field instead.
4. Check `config.prefer_superpowers`. If `auto`, probe for `superpowers:brainstorming`. Pick delegation or native loop.
5. Run the questioning loop (delegated or native) to collect the next skill's inputs from the manifest plus operator answers.
6. Append a `history[]` entry recording the routing decision.
7. Hand inputs to the recommended skill (or print them for the operator to invoke manually).

## When to use

- At session start, once `governance.yaml` exists. This is the entry point for ongoing governance work, equivalent in role to `using-superpowers` for the engineering loop.
- Whenever the operator asks "what should I do next" or "where am I in the chain."
- Whenever a recent skill output changed the manifest in a way that may shift the next-step recommendation (e.g., a freshly drafted PRFAQ moves the bet from Define toward Design).

## When NOT to use

- Before `governance.yaml` exists. Run `00-repo-state-import` first.
- When the operator already knows which Amazonian skill they want to invoke and is asking for help running it. Invoke the skill directly — the navigator's job is routing, not orchestration of the skill that has already been chosen.
- To "confirm the suite is happy" or "validate we're on track." That is exactly the confirmatory invocation `phase laundering` hides behind. The navigator must refuse and instead surface every `assumption`-tagged upstream field as a candidate `upstream_remediation` route.

## Inputs

```yaml
manifest_path:                  # required; absolute path to governance.yaml
operator_handle:                # required; recorded in history[]
session_intent:                 # optional; advisory only — e.g., "we want to review tenets"
prefer_superpowers_override:    # optional; auto | true | false; overrides manifest config for this invocation
```

## Required artifacts

- `governance.yaml` (must exist and validate against schema v1).

## Validation gates

| Gate | Pass criteria | If it fails |
|---|---|---|
| Manifest exists | File at `manifest_path` exists and is readable | Refuse; recommend running `00-repo-state-import` first |
| Schema valid | Manifest validates against `schema/governance.schema.json` | Refuse; surface the schema error; do not proceed |
| Chain state computable | State-machine maps the manifest to at least one recommended next action | Emit `routing_decision: block` with a "manifest is in an unrecognized state" finding |
| Upstream evidence resolves | For the recommended skill's `required_artifacts`, every manifest field they read has `evidence` in `{fact, inference}` with a resolving source | Demote to `routing_decision: upstream_remediation`; route to the producing skill |
| Not a confirmatory invocation | `session_intent` does not match patterns like "confirm", "validate we're fine", "everything good?" | Refuse and surface the strongest current `assumption`-tagged dependency as a finding |
| History append succeeds | New `history[]` entry written; manifest re-validates after append | Stop; surface the error rather than emit a corrupted manifest |

## Process

### 1. Validate

Read `manifest_path`. Validate against the JSON schema. Halt on failure with a precise pointer to the offending field.

### 2. Compute chain state

For each chain position in [`state-machine.yaml`](state-machine.yaml), compute whether the manifest satisfies the position's *preconditions* and what the *next required action* is. The state machine is deterministic; given a valid manifest, exactly one position is the current state.

Example position computations:

- `bet.prfaq_path` is null and `interviews[]` is empty → state `pre-discovery` → recommend `08-customer-interview-synthesis`.
- `bet.prfaq_path` is null and `interviews[]` has entries → state `discovery-complete` → recommend `01-working-backwards-prfaq`.
- PRFAQ exists, `success_metrics[]` is empty → state `prfaq-incomplete` → recommend revising `01-working-backwards-prfaq` (PRFAQ without metrics is incomplete).
- PRFAQ + metrics exist, `live_mechanisms[]` is empty → state `design-pending` → recommend `04-mechanism-designer`.
- WBR cadence due based on `live_mechanisms[].cadence` → recommend `05-weekly-business-review`.
- Tenets exist + bet has been active > one period boundary → recommend `10-tenets-review`.
- `period_goals[]` has a period whose `actual` is populated and there is no corresponding `prior_gradings[]` entry → recommend `11-ambitious-goal-grading`.

### 3. Phase-laundering check (second-axis)

For the recommended skill, enumerate its `required_artifacts` (from its SKILL.md) and trace each to a manifest field. For every traced field, check its `evidence` tag:

- `fact` with resolving source → pass.
- `inference` derived from `fact`-tagged predecessors → pass.
- `assumption` or `open_question` → **fail this gate**; demote the recommendation to `routing_decision: upstream_remediation` and replace the recommended skill with the *producing skill* for that field.

This is the load-bearing second-axis check that prevents recommending `10-tenets-review` against `assumption`-tagged tenets, or `11-ambitious-goal-grading` against `assumption`-tagged `stated_difficulty` (the `unstated` finding itself).

### 4. Select questioning mode

- If `prefer_superpowers_override` is set, use it.
- Else read `config.prefer_superpowers` from the manifest.
- `true` → delegate.
- `false` → native loop.
- `auto` → attempt skill-presence detection per [`delegation-contract.md`](delegation-contract.md). If detection succeeds, delegate. If detection is inconclusive, fall back to native and surface a `[Unverified]` note.

### 5. Run the questioning loop

**Delegation path:** invoke `superpowers:brainstorming` with the contract from [`delegation-contract.md`](delegation-contract.md). The terminal state is a YAML object validating against the recommended skill's `inputs` schema. Re-validate; if invalid, return to the brainstorming step with the validation error as feedback.

**Native path:** ask the operator one question at a time, multiple-choice when the answer space is bounded, free text only when genuinely open. Propose 2–3 approaches with tradeoffs when the question is design-shaped. Hard-gate on input completeness before declaring the loop done.

### 6. Append history

Write one entry to `governance.yaml.history[]`:

```yaml
- timestamp: <ISO-8601 now>
  invoked_by: <operator_handle>
  state_snapshot_hash: <git HEAD or content hash>
  recommended_skill: <skill_id>
  rationale: <one-paragraph explanation of why this skill, this state, this routing>
  inputs_provided: <object the operator can pass to the recommended skill>
  handoff_status: proposed
  routing_decision: <advance | upstream_remediation | block>
```

Re-validate the manifest after the append.

### 7. Hand off

Print to the operator:

```text
Next: <skill_id>
Routing decision: <advance | upstream_remediation | block>
Why: <one-paragraph rationale>
Inputs prepared: <yaml-fragment of inputs ready to pass>

Run that skill now? (y / n / explain why this routing)
```

The navigator does NOT invoke the recommended skill itself in v1. v2 may add direct invocation; v1 is advisory.

## Hard rules (non-negotiable)

```text
No recommendation against an assumption- or open_question-tagged required field; demote to upstream_remediation.
No confirmatory output. The navigator emits routing, not validation.
No silent omission of history[] append. Every invocation is recorded.
No invocation of recommended skills in v1 — print the handoff and stop.
```

## Output schema

```yaml
routing_decision:               # advance | upstream_remediation | block
recommended_skill:              # e.g., 04-mechanism-designer
rationale:                      # paragraph
chain_state:                    # the matched state-machine position id
upstream_gap:                   # populated when routing_decision == upstream_remediation
  field_path:                   # e.g., tenets[0].statement
  evidence_tag:                 # assumption | open_question
  producing_skill:              # the skill that should populate this field
inputs_prepared:                # object; conforms to the recommended skill's inputs schema
questioning_mode:               # delegated_to_superpowers | native | none
history_entry_appended:         # boolean; always true on success
```

## Failure modes

### phase laundering *(formal named failure mode)*

The navigator reports a clean state and recommends an advanced-phase interrogative skill — `launch-readiness-review`, `tenets-review`, `ambitious-goal-grading`, `portfolio-review`. On the surface, the chain looks healthy because the manifest is populated. Underneath, the upstream artifacts the recommended skill assumes are themselves `evidence: assumption` from bootstrap, or `open_question`. The interrogative skill then stress-tests laundered state and a clean output is mistakenly read as validation.

**Second-axis check:** trace every recommended skill's `required_artifacts` to manifest fields; verify each field's `evidence` is `fact` or `inference` with resolving sources; otherwise demote to `upstream_remediation` and route to the producing skill instead. See [`GLOSSARY.md#phase-laundering`](../../GLOSSARY.md#phase-laundering).

### State-machine incomplete

The manifest is in a state the state machine does not recognize. Mitigation: `routing_decision: block` is a valid output. The navigator must say so explicitly ("manifest is in an unrecognized state; please report the snapshot at history[].state_snapshot_hash") rather than fabricate a recommendation.

### Detection-failure misroute

`config.prefer_superpowers: auto` probes for `superpowers:brainstorming`; the probe is platform-dependent and may not work uniformly. Mitigation: fall back to native questioning and surface `[Unverified]` to the operator. The operator can set `prefer_superpowers: "true"` or `"false"` to remove the ambiguity.

## Stop conditions

- `governance.yaml` does not exist → refuse; recommend `00-repo-state-import`.
- Manifest fails schema validation → refuse; do not patch the manifest from the navigator.
- `session_intent` is confirmatory ("we're fine, right?", "validate we're on track") → refuse and surface the strongest `assumption`-tagged dependency as a finding.
- Phase-laundering check finds no resolvable upstream-remediation route (e.g., the producing skill is itself blocked by another `assumption`-tagged field) → emit `routing_decision: block` and surface the full upstream chain.

## Handoffs

| Routing decision | Hand off to |
|---|---|
| `advance` | The recommended Amazonian skill (01–13). Inputs are pre-populated. |
| `upstream_remediation` | The producing skill for the missing field. Recommendation includes which field needs to be elevated from `assumption` to `fact`/`inference`. |
| `block` | The operator. Manifest is in an unrecognized state; needs human review of `history[]` and possibly a `--reimport` via `00-repo-state-import`. |

For `advance` routings, the recommended skill consumes its normal inputs (now sourced from the manifest) and emits its normal output. Its emission may update manifest field groups (e.g., `01-working-backwards-prfaq` writes the PRFAQ and updates `bet.prfaq_path`). Each skill's manifest-update behavior is documented in that skill's `## Handoffs` section in its own SKILL.md. *[Unverified — existing skills 01–13 do not yet declare manifest-write behavior; that is v2 scope per RFC-001 §3.2 NG6.]*

## Optional observability emission

If the localhost observability stack at [`tools/observability/`](../../tools/observability/README.md) is running, this skill should emit events at each major phase of the routing pass so the operator can watch the reasoning unfold in real time. Emission is best-effort and silent on failure. The skill must complete its routing decision whether the observability server is up or not.

Recommended emission points:

```bash
source scripts/lib/emit-event.sh

amazonian_emit_event 14-lifecycle-navigator start

# After the state-machine match:
echo '{"matched_position":"operating-wbr-due"}' \
  | amazonian_emit_event 14-lifecycle-navigator progress

# When the phase-laundering check finds a gap:
echo '{"finding":"live_mechanisms[wbr-monday] evidence=assumption"}' \
  | amazonian_emit_event 14-lifecycle-navigator progress \
      "live_mechanisms[wbr-monday]" "" ""

# At the routing decision:
echo '{"routing_decision":"upstream_remediation","recommended_skill":"04-mechanism-designer"}' \
  | amazonian_emit_event 14-lifecycle-navigator end
```

See [`tools/observability/README.md`](../../tools/observability/README.md) for the event schema. The phase-laundering finding in particular benefits from being on the event log — it is the single most pedagogically valuable moment in a navigator session.

## Influences

- The orchestrator-with-hard-gates pattern is structurally similar to `using-superpowers` and `brainstorming` in the superpowers suite. The navigator borrows the pattern (one-question-at-a-time, propose-2-3-approaches, refuse to skip gates) without forking the implementation.
- The state-machine-driven routing is borrowed from build systems and finite-state-machine-driven workflow tools generally; the deterministic mapping from state to next action is the discipline, not a specific library.
- `phase laundering` as a named failure mode is suite-original, in the `*-laundering` family with `founder bias laundering` and `sandbagging laundering`.
