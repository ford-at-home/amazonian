# RFC-001: Deployment and Orchestration

| Field | Value |
|---|---|
| **Status** | Draft |
| **Authors** | (TBD) |
| **Created** | 2026-05-21 |
| **Supersedes** | — |
| **Superseded by** | — |
| **Tracking** | (TBD) |

---

## 1. Summary

Today the Amazonian suite assumes greenfield bets and treats each skill as independently invocable. Real users come with brownfield repos (existing code, implicit product theses, ad-hoc cadences) and want the chain to *manage them through the lifecycle*, not be reinvoked manually phase by phase. This RFC proposes four artifacts to close that gap:

1. **`governance.yaml`** — a versioned schema'd manifest at the repo root holding the lifted current state of a bet (tenets, success metrics, live mechanisms, period goals, dissent history, prior gradings, pointers to authored artifacts). Every field carries an evidence tag.
2. **`00-repo-state-import`** — a new **constructive** skill that reads a brownfield repo and helps the user populate `governance.yaml`. It refuses to emit unflagged claims. It is the entry door for *deploying* the suite onto an existing repo.
3. **`14-lifecycle-navigator`** — a new **interrogative** skill that reads `governance.yaml`, identifies the next required action in the chain, and either delegates the question-driven UX to `superpowers:brainstorming` (when present) or runs a minimal native questioning loop. Named failure mode: **`phase laundering`**. It is the running orchestrator.
4. **`scripts/install.sh`** — copies skills into the user-chosen scope (project or personal), scaffolds `governance.yaml` from a template, and prints whether superpowers was detected.

Together these answer three coupled product asks: *deploy the suite onto an existing repo*, *handle prior activity as the starting baseline*, and *manage the user through the PDLC flow*.

---

## 2. Motivation

### 2.1 The brownfield gap

Every skill in the chain reads structured inputs. `tenets-review` needs tenets. `ambitious-goal-grading` needs period goals + targets + actuals + a PRFAQ to compare against. `launch-readiness-review` needs a PRFAQ to diff the build state against. The chain assumes a populated state. There is currently no way to bring an existing repo into that state without writing every artifact from scratch, ahistorically — which is precisely the kind of vibes-not-mechanisms the suite was designed to prevent.

The honest description of an existing repo is: *we already have a customer model, we already have an implicit thesis, we already have mechanisms running, we already have goals — but none of them are contracted in the suite's shapes.* The bootstrap problem is structured lifting of that state, with explicit evidence tags so downstream skills don't treat lifted state as if it had passed governance gates retroactively.

### 2.2 The orchestration gap

The chain has 13 skills and a graph of dotted-line feedback edges. A user who has not memorized the README cannot know which skill to invoke next from their current state. There is no equivalent to `superpowers:using-superpowers` — a meta-skill that surveys state at session start, names next steps, and refuses to skip gates.

`superpowers:brainstorming` and `superpowers:writing-plans` provide that experience for the engineering loop (idea → ship a feature). The PDLC governance loop has no analog. Users either invoke the wrong skill (running `weekly-business-review` without a mechanism) or skip skills (running `launch-readiness-review` without a PRFAQ) or never start at all because they don't know where to begin.

### 2.3 The superpowers question

Many users (including the requesting user) have `superpowers` installed alongside Amazonian. Without integration, the two suites have no awareness of each other and the user gets two competing orchestrators at session start. With integration, Amazonian can delegate engineering-loop discipline (brainstorming, planning, TDD, verification) to superpowers while owning governance-loop discipline (PRFAQ, mechanisms, WBR, CoE, tenets, gradings, portfolio review).

---

## 3. Goals & non-goals

### 3.1 Goals

- **G1.** A brownfield repo can be deployed with the suite in a single command and end up with a `governance.yaml` reflecting its actual current state, with every field tagged for evidence.
- **G2.** A user invoking a single skill (`lifecycle-navigator`) at session start gets a deterministic next-action recommendation tied to their repo's current state.
- **G3.** When `superpowers` is installed, Amazonian delegates question-driven UX to it for skill input collection. When not installed, Amazonian provides equivalent native UX.
- **G4.** The suite's existing 13 skills are not modified. New behavior is additive.
- **G5.** Both new skills conform to `SKILL_DESIGN_PATTERN.md`. The navigator declares a named failure mode (`phase laundering`); the import skill describes its risk informally (`brownfield laundering`) because it is constructive.

### 3.2 Non-goals

- **NG1.** *Active orchestration* in v1. The navigator is *advisory*: it names the next required skill and records the handoff. Driving the questioning loop itself, dispatching subagents, and orchestrating multi-skill sessions is v2 work.
- **NG2.** *Auto-parsing* of existing READMEs / design docs into PRFAQ shape. The import skill is a structured Q&A; it does not infer PRFAQ contents from prose. (See `founder bias laundering` — automated inference of customer/value claims is exactly the failure the existing skill 08 exists to prevent.)
- **NG3.** *Auto-ingestion* of metrics from dashboards. The manifest stores pointers; populating live metrics is operator work.
- **NG4.** *Forking or upstream-contributing to superpowers.* Integration is via skill-presence detection plus a manifest preference flag. The superpowers repo is not touched.
- **NG5.** *Multi-bet repos* in v1. The manifest is single-bet; a repo with multiple bets uses multiple manifests (one per bet, in `bets/<bet-id>/governance.yaml`) — but the navigator only operates on one at a time. Cross-bet orchestration is a `portfolio-review` concern and out of scope here.
- **NG6.** *Modifications to existing skills.* If skill X needs to read a field from `governance.yaml`, that change is in scope for that skill's next revision, not this RFC. This RFC only adds.

---

## 4. Architecture overview

```text
                    ┌─────────────────────────────────────────┐
                    │       scripts/install.sh                │
                    │  • copy skills into scope               │
                    │  • scaffold governance.yaml stub        │
                    │  • detect superpowers; print mode       │
                    └──────────────────┬──────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │   governance.yaml (new artifact)        │
                    │   single source of truth for bet state  │
                    └──────────┬──────────────────┬───────────┘
                               │                  │
                  produces ◄───┘                  └───► reads
                               │                  │
                    ┌──────────┴───────────┐  ┌───┴─────────────────────┐
                    │ 00-repo-state-import │  │ 14-lifecycle-navigator  │
                    │ (constructive)       │  │ (interrogative)         │
                    │ entry door           │  │ running orchestrator    │
                    │ runs once at deploy  │  │ runs each session start │
                    └──────────────────────┘  └───┬─────────────────────┘
                                                  │
                                       delegates  │  if `superpowers:brainstorming`
                                       to ──────► │  is present; else uses native
                                                  │  questioning loop
                                                  ▼
                                           [next required Amazonian skill]
                                           (01–13, unchanged)
```

The two new skills are the *bookends of the bookends*: `00-repo-state-import` is how the suite enters a repo; `14-lifecycle-navigator` is how the suite runs in that repo across sessions. The existing 13 skills are unchanged.

---

## 5. Detailed design: `governance.yaml`

### 5.1 Location

- Default: `governance.yaml` at the repo root.
- Override: configurable via `scripts/install.sh --manifest-path <path>`; recorded in `.amazonian/config.yaml` for subsequent skill discovery.
- Multi-bet repos use `bets/<bet-id>/governance.yaml` (one per bet); see NG5.

### 5.2 Schema (v1)

```yaml
schema_version: 1
bet:
  id: string                          # kebab-case, unique within repo
  name: string                        # human-readable
  status: enum [active, paused, wound_down]
  prfaq_path: string | null           # relative to manifest
  six_pager_paths: [string]
  origin: enum [greenfield, brownfield]
  bootstrapped_at: ISO-8601 | null    # when 00-repo-state-import last ran
  bootstrapped_by: string | null      # operator handle

tenets:                                # consumed by 10-tenets-review
  - id: string
    statement: string
    evidence: enum [fact, assumption, inference, open_question]
    source: string | null              # link or citation if evidence=fact

success_metrics:                       # consumed by 04, 05, 09, 10, 11
  - id: string
    name: string
    target: number | string | null
    current: number | string | null
    unit: string
    measurement_source: string | null  # link to dashboard or query
    evidence: enum [fact, assumption, inference, open_question]

live_mechanisms:                       # consumed by 04, 05
  - id: string
    name: string
    cadence: string                    # e.g., "weekly", "monthly", "per-incident"
    spec_path: string | null           # link to 04-mechanism-designer output if exists
    inferred_from: string | null       # how we know this mechanism exists, if not spec'd
    evidence: enum [fact, assumption, inference, open_question]

period_goals:                          # consumed by 11
  - period_id: string                  # e.g., "2026-Q2"
    goals:
      - id: string
        statement: string
        target: number | string
        actual: number | string | null
        stated_difficulty: enum [stretch, committed, aspirational, unknown]
        evidence: enum [fact, assumption, inference, open_question]

prior_gradings:                        # consumed by 11
  - period_id: string
    graded_at: ISO-8601
    grading_path: string                # link to 11-ambitious-goal-grading output

dissent_log:                           # consumed by 12
  - id: string
    raised_at: ISO-8601
    against_action: string
    raised_by: string
    disposition: enum [addressed, accepted_with_tradeoff, deferred, pending]
    resolution_path: string | null

interviews:                            # consumed by 08
  - id: string
    path: string
    interviewee_role: string
    conducted_at: ISO-8601
    evidence_classification: enum [behavioral, attitudinal, mixed]

history:                               # appended by 14-lifecycle-navigator
  - timestamp: ISO-8601
    invoked_by: string                 # operator handle
    state_snapshot_hash: string        # git hash or content hash
    recommended_skill: string          # e.g., "04-mechanism-designer"
    rationale: string
    inputs_provided: object            # what the navigator handed to the next skill
    handoff_status: enum [proposed, executed, declined]

config:
  prefer_superpowers: enum [auto, true, false]   # default: auto
  amazonian_skill_scope: enum [project, personal]
```

### 5.3 Evidence tagging

Every claim-bearing field carries an `evidence` enum from the suite's existing assumption-tag vocabulary in `GLOSSARY.md`:

- `fact` — verifiable with a source
- `assumption` — believed true, untested
- `inference` — derived from other facts
- `open_question` — explicit gap requiring follow-up

This is the load-bearing discipline that prevents `brownfield laundering`. Skills downstream of the manifest **may refuse to operate** on fields tagged `assumption` or `open_question` if those gates are critical (e.g., `10-tenets-review` cannot honestly stress-test tenets that are themselves `assumption`-tagged; it must surface that as the first finding).

### 5.4 Validation

A separate schema file ships at `schema/governance.schema.json` for tooling. The install script runs a one-shot validation after scaffolding. The navigator runs validation on every read.

---

## 6. Detailed design: `00-repo-state-import`

### 6.1 Conformance to `SKILL_DESIGN_PATTERN.md`

| Field | Value |
|---|---|
| `name` | `repo-state-import` |
| `purpose` | Lift a brownfield repo's current state into `governance.yaml` with explicit evidence tags on every field. |
| `category` | constructive |
| `inputs` | repo path; optional pointer to existing artifacts (READMEs, design docs, dashboards); operator handle |
| `required_artifacts` | none (this is the entry door; nothing exists yet) |
| `process_steps` | survey → interview operator → tag evidence → draft manifest → reviewer pass → emit |
| `validation_gates` | every field has an evidence tag; no `fact` tag without a source; manifest passes schema validation |
| `reviewer_agent` | `02-amazon-writing-linter` on free-text fields (statements, rationales) |
| `output_schema` | `governance.yaml` conforming to schema v1 |
| `failure_modes` | brownfield laundering (informal; see §6.2); operator over-claim on `fact` tags; manifest drift if not re-run |
| `stop_conditions` | refuse to emit if any field would be untagged; refuse to set `evidence: fact` without a `source`; refuse to operate on a repo that already has a valid manifest unless `--reimport` is passed |
| `follow_up_mechanism` | hand off to `14-lifecycle-navigator` for next-step recommendation |

### 6.2 Named risk: `brownfield laundering` *(informal)*

> The lifted manifest's surface signal (every field populated, schema valid, downstream skills runnable) hides the structural failure that the populated state never actually passed any governance gate. Downstream skills, reading the manifest, treat lifted assumptions as if they were the output of the constructive skills that should have produced them. The skill exists to refuse evidence-blind population: every field carries a tag, and `fact` requires a source.

The spine technically does not require a constructive skill to declare a named failure mode. We declare it informally (in the SKILL.md `## Failure modes` section and in `GLOSSARY.md`) because it is a real risk and naming it makes downstream skills' assumption-handling cleaner. We do *not* add it to the formal `## Named failure modes` index — that surface remains for interrogative skills per the spine.

### 6.3 Process (sketch)

1. **Survey phase.** Read the repo's top-level files (READMEs, design docs, recent commits, existing `docs/` content). Build an inventory of *evidence candidates* — things that could become tagged fields. Do not lift them yet.
2. **Interview phase.** For each major field group (`tenets`, `success_metrics`, `live_mechanisms`, `period_goals`, `interviews`), ask the operator structured questions:
   - "Do you currently have stated product tenets? If yes, where? If no, can you state them now?" — evidence resolves to `fact` (with path) or `assumption` (newly stated, untested).
   - "What metrics do you measure weekly? Where are they tracked? What's the current value?" — evidence resolves based on dashboard linkage.
   - "What recurring forums exist for this bet? Standups? Reviews? Are they documented anywhere?" — evidence resolves accordingly.
3. **Tag phase.** Every collected field gets an evidence tag. Refuse to proceed if any tag is missing.
4. **Reviewer pass.** Invoke `02-amazon-writing-linter` on free-text fields to strip vagueness and surface unsupported claims.
5. **Emit phase.** Write `governance.yaml`. Append a `history[]` entry recording the bootstrap.
6. **Handoff.** Print: *"Manifest written. Run `14-lifecycle-navigator` to see the next required skill."*

### 6.4 Files shipped

```text
skills/00-repo-state-import/
├── SKILL.md
├── interview-questions.yaml          # structured questions per field group
├── examples/example-bootstrap.yaml   # worked example for a hypothetical brownfield bet
└── templates/governance-template.yaml
```

---

## 7. Detailed design: `14-lifecycle-navigator`

### 7.1 Conformance to `SKILL_DESIGN_PATTERN.md`

| Field | Value |
|---|---|
| `name` | `lifecycle-navigator` |
| `purpose` | Read `governance.yaml`, identify the next required skill in the chain given current state, and either delegate the input-collection UX to `superpowers:brainstorming` or run a minimal native questioning loop. Record the handoff. |
| `category` | interrogative |
| `inputs` | path to `governance.yaml`; optional override of `prefer_superpowers` config |
| `required_artifacts` | `governance.yaml` (validates against schema v1 before reading) |
| `process_steps` | validate manifest → compute chain state → identify next required skill → check for superpowers → route question-driven UX → record handoff |
| `validation_gates` | manifest schema valid; no critical `evidence: open_question` fields for the path being recommended; recommended skill's `required_artifacts` resolvable from manifest |
| `reviewer_agent` | self-check against schema + chain state machine; no external reviewer needed (this is a routing skill) |
| `output_schema` | recommendation object (next_skill, rationale, inputs_to_provide, pending_reviews) + appended `history[]` entry in manifest |
| `failure_modes` | **phase laundering** (see §7.2); state staleness if manifest not maintained; misrouting if chain state machine is incomplete |
| `stop_conditions` | refuse to recommend a skill whose required inputs are tagged `assumption` or `open_question` without surfacing that as the recommendation; refuse confirmatory invocation ("everything's fine, right?") |
| `follow_up_mechanism` | the named Amazonian skill it routes to (01–13); on completion, that skill or the operator returns to navigator for next handoff |

### 7.2 Named failure mode: `phase laundering`

> **Surface signal:** the navigator reports a clean state and recommends an advanced phase skill (e.g., `launch-readiness-review`, `tenets-review`, `ambitious-goal-grading`).
>
> **Structural failure underneath:** the upstream artifacts the recommended skill assumes (PRFAQ for LRR; tenets for tenets-review; period goals + prior PRFAQ for grading) are themselves `evidence: assumption` from the bootstrap, or are missing entirely. The chain looks healthy on its face because the manifest is populated, but the foundation under the recommended skill is laundered brownfield state.
>
> **Second-axis check:** for every recommendation, the navigator must trace the recommended skill's `required_artifacts` to manifest fields and verify they are either `evidence: fact` or `evidence: inference` (with the sources resolving). Recommendations against `evidence: assumption` or `open_question` are demoted to *"first, resolve upstream gap X"* and the user is routed to the constructive skill that produces field X — not the interrogative skill that would have stress-tested its already-laundered version.

### 7.3 Native questioning loop (when superpowers absent)

When `config.prefer_superpowers == false`, or when `auto` detection finds no `superpowers:brainstorming` skill in the environment, the navigator runs a minimal native questioning loop borrowed from `brainstorming/SKILL.md`'s observable patterns:

- **One question per message.** No batching.
- **Multiple choice preferred.** Free text only when the answer space is genuinely open.
- **Propose 2–3 approaches with tradeoffs.** Never present a single recommendation as a fait accompli.
- **Hard-gate on input completeness.** Refuse to dispatch to the downstream skill until all of its `required_artifacts` are either fact-tagged or explicitly accepted as assumption with operator acknowledgment.

This is not a fork of superpowers and does not claim parity. It is the minimum equivalent UX so Amazonian remains useful in environments without superpowers.

### 7.4 Superpowers delegation (when superpowers present)

When `config.prefer_superpowers == true`, or when `auto` detection finds `superpowers:brainstorming`, the navigator:

1. Announces: *"Superpowers detected; delegating input collection to `superpowers:brainstorming`."*
2. Hands off with a structured contract:
   - **Goal:** populate inputs for `<next required Amazonian skill>`.
   - **Terminal state:** brainstorming's design-doc artifact, structured as the next skill's `inputs` schema.
   - **Constraint:** evidence tags on every field, per Amazonian discipline.
3. Resumes after brainstorming completes; validates the produced inputs against the next skill's schema; appends handoff to `history[]`; invokes the next skill or hands the inputs back to the operator.

### 7.5 Chain state machine

The navigator implements a deterministic state machine over manifest contents. Rough sketch:

| If manifest state... | Then recommend... |
|---|---|
| `bet.prfaq_path` is null and `interviews` is empty | `08-customer-interview-synthesis` |
| `bet.prfaq_path` is null and `interviews` is non-empty | `01-working-backwards-prfaq` |
| PRFAQ exists, `success_metrics` is empty | back to `01-working-backwards-prfaq` (PRFAQ incomplete) |
| PRFAQ + metrics exist, `live_mechanisms` is empty | `04-mechanism-designer` |
| Mechanism exists, no recent WBR | `05-weekly-business-review` |
| WBR shows persistent variance | `06-correction-of-errors` |
| Build state diverges from PRFAQ contract | `09-launch-readiness-review` |
| Tenets exist but unreviewed in current period | `10-tenets-review` |
| Period closed, goals exist, no grading | `11-ambitious-goal-grading` |
| Multiple bets exist with manifests; cross-bet review window | `13-portfolio-review` |
| Pending action with no recent dissent canvass | `12-dissent-before-commit` |

Full state machine is defined in `skills/14-lifecycle-navigator/state-machine.yaml` (machine-readable) and rendered in the SKILL.md for human review.

### 7.6 Files shipped

```text
skills/14-lifecycle-navigator/
├── SKILL.md
├── state-machine.yaml
├── delegation-contract.md          # the handoff schema to superpowers:brainstorming
└── examples/example-navigation.md
```

---

## 8. Detailed design: `scripts/install.sh`

### 8.1 Behavior

```text
Usage: install.sh [--scope project|personal] [--manifest-path PATH] [--reimport]

Default: --scope personal

Steps:
  1. Validate target directory is a git repo.
  2. Detect installed plugin caches; report presence/absence of:
     • superpowers
     • cli-for-agents
     • parallel
     (informational; only superpowers affects navigator behavior)
  3. Copy skills/* into the chosen scope:
     • personal → ~/.cursor/skills/
     • project  → ./.cursor/skills/
  4. If governance.yaml does not exist (or --reimport):
     • Scaffold governance.yaml stub from template
     • Set bet.origin = brownfield
     • Set config.prefer_superpowers = auto
  5. Print next-step message:
     • "Run skill 00-repo-state-import to populate the manifest."
     • "After that, run skill 14-lifecycle-navigator to see the next phase."
```

### 8.2 Idempotence

Re-running the script with no flags must be a no-op on an already-deployed repo. `--reimport` is the explicit escape hatch. This is the same discipline applied to mechanisms in the suite — re-invocation should not create silent drift.

### 8.3 Files shipped

```text
scripts/
├── install.sh
├── lib/
│   ├── detect-plugins.sh
│   └── scaffold-manifest.sh
└── templates/
    └── governance-template.yaml
```

---

## 9. Superpowers integration: mechanics

### 9.1 Detection

Two mechanisms, in priority order:

1. **`config.prefer_superpowers`** in `governance.yaml`. Values: `auto` (default), `true`, `false`. `true` and `false` are unconditional; `auto` falls through to (2).
2. **Skill-presence probe.** The navigator attempts to discover a skill named `superpowers:brainstorming` (or `brainstorming` in environments without namespace prefixes) at session start. Mechanism is platform-dependent and documented as `[Unverified]` in v1 until tested on Cursor / Claude Code / Copilot CLI.

If detection fails inconclusively, the navigator falls back to native questioning and prints: *"Could not verify superpowers presence; using native questioning. Set `config.prefer_superpowers: true` in `governance.yaml` to force delegation."*

### 9.2 Handoff contract

The delegation contract is published at `skills/14-lifecycle-navigator/delegation-contract.md`. It specifies:

- The navigator hands superpowers a **goal statement** (populate inputs for skill X), an **inputs schema** (X's required inputs typed per `governance.yaml`'s vocabulary), and a **terminal-state requirement** (a YAML object validating against the inputs schema).
- Superpowers' `brainstorming` skill runs its normal flow (clarifying questions → propose approaches → present design → write spec → user-review gate → invoke `writing-plans`).
- The navigator intercepts the `writing-plans` handoff (or the design-doc terminal state) and re-validates against the inputs schema before invoking the Amazonian skill.

This contract is one-way: Amazonian knows about superpowers' shape; superpowers knows nothing about Amazonian. Superpowers receives a structured task and returns a structured artifact, same as any other invocation.

### 9.3 Precedence at session start

If both `using-superpowers` and `lifecycle-navigator` activate at session start:

- **If `governance.yaml` exists**: `lifecycle-navigator` runs first. It is the entry point for the *governance* loop, which is the broader concern. If the navigator's recommendation requires engineering work, it can hand off into `using-superpowers`' loop downstream.
- **If `governance.yaml` does not exist**: `using-superpowers` (if installed) runs first. Amazonian is dormant until `00-repo-state-import` is run.

This precedence is encoded in `lifecycle-navigator`'s frontmatter `description` so that the agent's skill-selection logic resolves it deterministically. *[Unverified — depends on agent-platform-specific skill-priority semantics; may need testing.]*

---

## 10. Named failure modes (summary)

| Skill | Name | Formal? | Surface signal | Second-axis check |
|---|---|---|---|---|
| `00-repo-state-import` | `brownfield laundering` | Informal (constructive skill) | Manifest fully populated, schema valid, downstream skills runnable | Every field has an evidence tag; `fact` requires a source; `assumption`-tagged fields propagate as constraints to downstream skill recommendations |
| `14-lifecycle-navigator` | `phase laundering` | Formal (interrogative skill) | Navigator reports clean state, recommends advanced-phase skill | Trace recommended skill's `required_artifacts` to manifest fields; demote to upstream-gap remediation if any are `assumption` / `open_question` |

`phase laundering` is added to `GLOSSARY.md#named-failure-modes-cross-reference`. `brownfield laundering` is added to a new `GLOSSARY.md#informal-named-risks` section (or similar — exact section name TBD during implementation).

---

## 11. Skill input ↔ manifest field mapping

| Skill | Reads from manifest |
|---|---|
| `01-working-backwards-prfaq` | `bet`, `interviews[]` (synthesis output staged here) |
| `03-six-page-narrative` | `bet`, `bet.prfaq_path` |
| `04-mechanism-designer` | `success_metrics[]`, `bet` |
| `05-weekly-business-review` | `live_mechanisms[]`, `success_metrics[]` |
| `06-correction-of-errors` | `bet`, (incident from outside manifest) |
| `08-customer-interview-synthesis` | `interviews[]` |
| `09-launch-readiness-review` | `bet.prfaq_path`, repo HEAD state (outside manifest) |
| `10-tenets-review` | `tenets[]`, `bet.prfaq_path`, `success_metrics[]` |
| `11-ambitious-goal-grading` | `period_goals[]`, `prior_gradings[]`, `bet.prfaq_path` |
| `12-dissent-before-commit` | `dissent_log[]`, (action from outside manifest) |
| `13-portfolio-review` | reads every `bets/<bet-id>/governance.yaml` |
| `02-amazon-writing-linter` | — (cross-cutting; takes input directly) |
| `07-leadership-principles-reviewer` | — (cross-cutting; takes input directly) |
| `00-repo-state-import` | — (produces the manifest; reads none of it) |
| `14-lifecycle-navigator` | reads the whole manifest |

This table is the source of truth for what the manifest must contain. Schema fields that no skill reads should be deleted in subsequent RFC revisions; skills that need fields not listed here trigger schema bumps to v2.

---

## 12. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Skill-presence detection mechanism is platform-dependent and may not work uniformly across Cursor, Claude Code, Copilot CLI, Gemini CLI | Medium | Medium | Manual override via `config.prefer_superpowers: true\|false`; auto detection labeled `[Unverified]` in v1 until tested |
| R2 | The navigator's state machine misroutes due to incomplete coverage of manifest states | High | Medium | State machine is schema'd in `state-machine.yaml`; new states added via explicit RFC revision; "unknown state" is itself a valid output ("manifest is in a state I don't recognize — please report") |
| R3 | `governance.yaml` drifts from repo reality as engineering work proceeds without manifest updates | High | High | The manifest itself becomes an audit artifact; `tenets-review` and `launch-readiness-review` already gate on `PRFAQ drift`-style checks and can be extended to flag manifest drift; out of scope for v1 but tracked |
| R4 | Two-orchestrator precedence (superpowers vs navigator) fails when the agent platform doesn't honor skill `description` priority hints | Medium | Low | Documented user-facing workaround: explicit invocation ("use lifecycle-navigator"); not a v1 blocker |
| R5 | The native questioning loop diverges from superpowers' patterns over time, creating two experiences for the same user | Medium | Low | Native loop is deliberately minimal (one-question-per-message + multiple-choice + 2–3 approaches); does not attempt to replicate brainstorming's full surface |
| R6 | Operators over-claim on `fact` evidence tags because the source field is hard to verify | Medium | High | The linter pass in `00-repo-state-import` checks that every `fact` tag has a non-null `source`; future work could verify links resolve, parse cited docs, etc. (out of scope for v1) |
| R7 | The bootstrap interview becomes a quiz nobody completes | High | High | Skill must support *partial mode*: populate what's evidenced, mark gaps as `open_question`, only fail loudly on gaps that would block the *next* skill the operator wants to run |

---

## 13. Open questions

| # | Question | Notes |
|---|---|---|
| OQ1 | Should `governance.yaml` live at repo root or in `.amazonian/governance.yaml`? | Tradeoff: visibility vs root-clutter. Default in this RFC is root for visibility. Re-evaluate after first user feedback. |
| OQ2 | Should the navigator support a dry-run mode that prints the recommendation but doesn't append to `history[]`? | Likely yes; v1 default behavior TBD. |
| OQ3 | Should multi-bet repos use `bets/<bet-id>/governance.yaml` or a single `governance.yaml` with `bets[]`? | This RFC picks per-bet files. Single-file might compose better with `portfolio-review`. Revisit in RFC-002 if/when multi-bet support is built. |
| OQ4 | Native questioning loop: should it record sessions to disk for replay/audit? | Probably yes; matches the suite's audit-trail commitment. v1 scope TBD. |
| OQ5 | Should `00-repo-state-import` support continuous lifting (re-run periodically to catch drift) vs one-shot bootstrap? | One-shot in v1 per `--reimport` flag; continuous mode is a candidate v2 feature once drift detection is real. |

---

## 14. Implementation phasing

### v1 (this RFC)

1. `governance.yaml` schema + JSON schema for validation
2. `00-repo-state-import` skill (constructive; informal `brownfield laundering`)
3. `14-lifecycle-navigator` skill (interrogative; formal `phase laundering`; advisory only)
4. `scripts/install.sh` (idempotent; detects superpowers)
5. Updates to `GLOSSARY.md` and `vocabulary.yaml` for the two new failure modes
6. Updates to `LIFECYCLE.md` to position the two new skills in the chain
7. Updates to `README.md` skills table to add rows 00 and 14
8. New whiteboard infographic update? *(optional; deferred unless requested)*

### v2 (future, not in scope here)

- Active orchestration: the navigator drives the questioning loop itself, not just recommends.
- Subagent dispatch from the navigator (when superpowers' subagent skills are present).
- Continuous-mode `repo-state-import` with drift detection.
- Multi-bet manifest unification.
- Auto-parsing of READMEs / design docs into PRFAQ candidate inputs (gated behind `founder bias laundering` review).

---

## 15. Compliance check against `SKILL_DESIGN_PATTERN.md`

| Spine field | `00-repo-state-import` | `14-lifecycle-navigator` |
|---|---|---|
| name | ✓ | ✓ |
| purpose (one sentence) | ✓ §6.1 | ✓ §7.1 |
| inputs (named, typed) | ✓ §6.1 | ✓ §7.1 |
| required_artifacts | ✓ (none, by design) §6.1 | ✓ (`governance.yaml`) §7.1 |
| process_steps (ordered, deterministic) | ✓ §6.3 | ✓ §7.1 |
| validation_gates | ✓ §6.1, §6.3 | ✓ §7.1 |
| reviewer_agent | ✓ (`02-amazon-writing-linter`) | ✓ (self-check + schema validation) |
| output_schema | ✓ (governance.yaml schema v1) | ✓ (recommendation + history entry) |
| failure_modes | ✓ informal `brownfield laundering` | ✓ formal `phase laundering` |
| stop_conditions | ✓ §6.1 | ✓ §7.1 |
| follow_up_mechanism | ✓ (hands off to navigator) | ✓ (hands off to next required Amazonian skill) |
| category (constructive / interrogative) | constructive | interrogative |
| Length ≤ 500 lines (target ≤ 250) | enforced at implementation time | enforced at implementation time |

Neither skill collapses constructive+interrogative responsibilities (the explicit disqualifier from `LIFECYCLE.md#rejected-skill-categories`). Both name a downstream artifact or skill that consumes their output. Neither is "advice" or "considerations" without structure.

---

## 16. Approval

This RFC requires sign-off on:

- **Scope**: the four-artifact bundle is right-sized for v1.
- **Architecture**: two new skills + manifest + install script; no modifications to existing 13 skills.
- **Named failure modes**: `phase laundering` (formal) and `brownfield laundering` (informal).
- **Superpowers integration model**: detection + delegation contract, no fork.
- **Phasing**: advisory navigator in v1; active orchestration deferred to v2.

After approval, implementation proceeds as a sequence of small commits, each producing working, testable artifacts in the order: schema → import skill → install script → navigator skill → docs updates.
