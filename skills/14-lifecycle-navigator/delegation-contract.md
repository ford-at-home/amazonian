# Delegation Contract

How `14-lifecycle-navigator` hands off question-driven UX to `superpowers:brainstorming` when it is present in the agent's environment.

## Direction

**Amazonian → Superpowers (one-way).** Amazonian knows about superpowers' shape and adapts to it. Superpowers does not know about Amazonian — it receives a structured task and emits a structured artifact, the same way it would for any other invocation. This asymmetry is deliberate. It means:

- Amazonian is fully usable without superpowers installed (native fallback).
- Superpowers does not need to be modified or forked.
- Amazonian's release cadence is decoupled from superpowers'.

## Detection mechanism

The navigator selects delegation mode in this order:

1. **Explicit override.** If the navigator's `prefer_superpowers_override` input is set (`true`, `false`, or `auto`), it wins.
2. **Manifest config.** `governance.yaml.config.prefer_superpowers`. Values:
   - `"true"` → always delegate.
   - `"false"` → always use native loop.
   - `auto` (default) → fall through to (3).
3. **Skill-presence probe.** Attempt to discover a skill named `superpowers:brainstorming` (or `brainstorming` in environments without namespace prefixes). The mechanism is platform-dependent:
   - **Cursor**: read available skills via the Skill discovery API. *[Unverified — exact API surface may vary by Cursor version.]*
   - **Claude Code**: check the loaded skill registry. *[Unverified.]*
   - **Copilot CLI**: query the `skill` tool's index. *[Unverified.]*
   - **Other platforms**: fall through to (4).
4. **Fallback.** If detection is inconclusive, use the native loop and emit a `[Unverified]` note: *"Could not verify superpowers presence; using native questioning. Set config.prefer_superpowers to 'true' or 'false' in governance.yaml to remove this check."*

## Handoff contract

When the navigator delegates, it hands superpowers' `brainstorming` skill the following structured task:

```yaml
goal: "Populate inputs for Amazonian skill: <skill_id>"

context:
  bet_id: <governance.yaml.bet.id>
  bet_name: <governance.yaml.bet.name>
  manifest_path: <absolute path>
  chain_state: <state-machine position id, e.g., design-pending>

target_skill:
  id: <e.g., 04-mechanism-designer>
  inputs_schema: <YAML object describing the skill's required inputs>
  validation_gates: <YAML list of the skill's validation gates from its SKILL.md>

evidence_discipline:
  "Every populated field in the terminal artifact must carry an evidence tag
   from {fact, assumption, inference, open_question}. Fields tagged `fact`
   must have a non-null source. This is the same discipline applied across
   the Amazonian suite; do not relax it."

terminal_state_requirement:
  "Brainstorming's terminal artifact must be a YAML object validating against
   target_skill.inputs_schema. The navigator re-validates after handback;
   if validation fails, the operator is re-routed to brainstorming with the
   validation error as feedback."

constraints:
  - "Do not invent values not supplied by the operator."
  - "Do not infer customer/product/value claims from prose; that is 08-customer-interview-synthesis's responsibility."
  - "Multi-step decomposition is fine; each step's output is tagged."

handoff_after_completion:
  "Return control to lifecycle-navigator. Navigator re-validates the inputs,
   appends a history[] entry to governance.yaml, and either invokes the
   target skill (v2) or prints the prepared inputs for the operator (v1)."
```

## What superpowers sees vs. what Amazonian sees

| Phase | Superpowers' view | Amazonian's view |
|---|---|---|
| Pre-handoff | Receives a task with goal + inputs_schema + constraints | Knows the chain state and the next required skill; needs structured inputs |
| During brainstorming | Runs its normal flow: clarifying questions, propose approaches, present design, write spec, user-review gate | Yields control; trusts superpowers' patterns for the question loop |
| Terminal state | About to invoke `writing-plans` (its normal terminal handoff) | Intercepts the design-doc artifact instead of letting writing-plans run; re-validates against `inputs_schema` |
| Post-handoff | Returns; not aware of what comes next from Amazonian's perspective | Re-validates, appends history[], hands prepared inputs to the operator (v1) or invokes target skill (v2) |

The interception of `writing-plans` is critical. Superpowers' `brainstorming` normally terminates by invoking `writing-plans` to produce an implementation plan. Amazonian does not want an implementation plan — it wants structured inputs. The navigator must:

1. Read the design-doc artifact that brainstorming wrote (at `docs/superpowers/specs/...`).
2. Project the relevant fields onto the target skill's inputs schema.
3. Skip the `writing-plans` invocation that would otherwise be brainstorming's next step.

This projection is the **only** Amazonian-side logic that needs to know about superpowers' artifact format. Everything else is the generic structured-task pattern.

## Precedence at session start

When both `using-superpowers` and `lifecycle-navigator` would activate at session start:

- **If `governance.yaml` exists**: `lifecycle-navigator` runs first. It is the entry point for the governance loop. If its recommendation requires engineering work downstream (e.g., the recommended skill is `04-mechanism-designer` which then needs implementation), the navigator can hand into superpowers' engineering loop at that point.
- **If `governance.yaml` does not exist**: `using-superpowers` (if installed) runs first. Amazonian is dormant until `00-repo-state-import` is invoked.

This precedence is encoded in the navigator's frontmatter `description` so the agent's skill-selection logic resolves it deterministically. *[Unverified — depends on agent-platform-specific skill-priority semantics; may need testing on each platform.]*

## What the contract does NOT cover

- Subagent dispatch from the navigator. v2 work. The navigator in v1 is advisory; it prints prepared inputs and stops. v2 may invoke `superpowers:subagent-driven-development` to actually run the target skill in a fresh subagent.
- Multi-bet orchestration. v2.
- Continuous re-import (drift detection). v2.

These deferrals are documented in [`docs/rfcs/RFC-001-deployment-and-orchestration.md`](../../docs/rfcs/RFC-001-deployment-and-orchestration.md) §14.

## Versioning

This contract is v1. Breaking changes to the contract require an RFC and a schema bump in `governance.yaml`. Non-breaking additions (new optional fields, new context keys) do not require an RFC but must be documented in this file with a version note.
