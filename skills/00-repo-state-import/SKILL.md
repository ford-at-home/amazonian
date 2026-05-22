---
name: repo-state-import
description: Lift a brownfield repo's current governance state into a structured governance.yaml manifest. Conducts a guided interview over tenets, success metrics, live mechanisms, period goals, dissent history, and prior interviews; refuses to emit any field without an evidence tag from the set fact / assumption / inference / open_question; refuses to claim a field is a fact without a non-null source. The informal named risk is brownfield laundering — a populated manifest read by downstream skills as if it had passed governance gates when it never did. Use when first deploying the Amazonian suite onto an existing repo, or when re-importing after material changes; or when the user mentions "bootstrap", "onboard a repo", "lift state", "governance.yaml", "import existing state", or "brownfield deploy".
category: constructive
required_reviews:
  - amazon-writing-linter
---

# Repo State Import

Lift a brownfield repo's current state into [`governance.yaml`](../../scripts/templates/governance-template.yaml). This skill is the **entry door** to the suite — it runs once when the suite is first deployed onto a repo with prior activity. Every claim it emits carries an evidence tag; every `evidence: fact` carries a source. Without that discipline, downstream skills treat lifted assumptions as governance-grade artifacts. See [`brownfield laundering`](../../GLOSSARY.md#brownfield-laundering).

This skill is constructive — it produces a manifest — but its production discipline is interrogative in spirit: it refuses to populate fields it cannot evidence, and tags everything that does not survive operator interrogation as `assumption` or `open_question` instead of inferring confident-sounding values.

## Quick start

1. Confirm the repo is a git repository and that no `governance.yaml` already exists at the manifest path (or pass `--reimport` to overwrite).
2. Survey the repo's existing artifacts (READMEs, design docs, recent commits). Build a candidate-evidence list. Do not lift yet.
3. Walk the operator through the interview questions in [`interview-questions.yaml`](interview-questions.yaml), field group by field group.
4. Tag every collected value with an evidence enum. Refuse to proceed past any field that cannot be tagged.
5. Run `amazon-writing-linter` over free-text statements (tenet statements, goal statements, mechanism descriptions). Strip vagueness.
6. Emit the manifest at the configured path, set `bet.origin = brownfield`, set `bet.bootstrapped_at` and `bet.bootstrapped_by`.
7. Hand off to `14-lifecycle-navigator` for the next-step recommendation.

## When to use

- Deploying the Amazonian suite onto a repo that has prior commits, an implicit product thesis, or active operating cadences.
- Re-importing state after material change (with `--reimport`) — e.g., a strategic pivot, change in operating cadence, or a new period of goals.
- The user says: "bootstrap", "onboard the repo", "lift current state", "set up governance", "deploy the suite", "import what we already have", "brownfield deploy".

## When NOT to use

- Greenfield bets where the PRFAQ is being authored from scratch under the suite's governance — the suite's normal authoring chain (`08` → `01` → `04` → ...) already covers that case. The manifest is still populated, but field by field as each authoring skill emits its output, not all at once.
- The repo already has a valid `governance.yaml` and the operator wants to add or revise a single field — edit the manifest directly or invoke the specific producing skill. Re-running the full import on a populated manifest invites laundering.
- The operator wants help inferring what the customer wants from existing docs. That is `08-customer-interview-synthesis`'s job, and this skill must not impersonate it. The import skill records what interviews exist; it does not synthesize them.

## Inputs

```yaml
repo_path:                      # required; absolute path to the git repo
operator_handle:                # required; will be recorded as bootstrapped_by
manifest_path:                  # optional; defaults to <repo_path>/governance.yaml
mode:                           # full | partial — partial allows operator to skip field groups marked unknown
reimport:                       # boolean; default false; required true to overwrite an existing manifest
candidate_evidence:             # optional; output of the Survey phase passed back in for the Interview phase
```

## Required artifacts

None. This skill is the entry door; no prior artifacts in the suite are required. (It does require that the operator can answer questions about the bet — see the bootstrap-quiz failure mode below.)

## Validation gates

| Gate | Pass criteria | If it fails |
|---|---|---|
| Repo is a git repo | `git -C <repo_path> rev-parse --git-dir` exits 0 | Refuse; ask operator to run inside a git repo |
| No existing manifest | `manifest_path` does not exist OR `reimport: true` | Refuse; surface existing manifest path |
| Every field has evidence | Each populated leaf field carries `evidence` in `{fact, assumption, inference, open_question}` | Refuse to emit; surface the untagged field |
| `fact` has a source | Every field with `evidence: fact` has a non-null, non-empty `source` | Demote to `assumption` or require source from operator |
| `bet.id` is kebab-case | Matches `^[a-z0-9][a-z0-9-]*[a-z0-9]$` | Re-prompt |
| Schema validation | Final manifest validates against `schema/governance.schema.json` | Surface the schema error; do not write |
| Linter pass on free text | `amazon-writing-linter` ran clean on tenet statements, goal statements, mechanism descriptions | Apply linter revisions; re-run gate |
| Partial-mode discipline | If `mode: partial`, every skipped field group is recorded as `open_question` in `history[]`, not silently omitted | Record the gap explicitly |

## Process

### 1. Survey (read, do not lift)

Walk the repo and enumerate **candidate-evidence sources** without populating any manifest field yet:

- Top-level files: `README.md`, `ARCHITECTURE.md`, `TENETS.md`, `OKRS.md`, `STRATEGY.md`, anything in `docs/`.
- Recent commit log (last 50): does it reveal an implicit operating cadence (e.g., weekly merges, release tags, retro notes)?
- Existing dashboards or metric references in code/docs.
- Interview transcripts or research notes in `interviews/`, `research/`, `discovery/`.

Output of this phase: a `candidate_evidence` list with `{field_group, source_path, snippet, confidence}` for each candidate. Do not commit to any value yet.

### 2. Interview (one field group at a time)

For each field group in [`interview-questions.yaml`](interview-questions.yaml) — `bet`, `tenets`, `success_metrics`, `live_mechanisms`, `period_goals`, `interviews`, `dissent_log` — ask the operator the structured questions in order. **Never** present multiple field groups in one message. One group, then wait, then next.

For every operator answer:

- If the operator points to an existing artifact (`docs/tenets.md`, a dashboard URL, a research file), confirm the path or URL resolves, then tag `evidence: fact` and set `source`.
- If the operator states a value without a written source, tag `evidence: assumption` and leave `source: null`.
- If the operator derives a value from other facts already collected, tag `evidence: inference`.
- If the operator does not know, tag `evidence: open_question`. Do not invent a value.

### 3. Tag enforcement

Before writing any field to the manifest, scan: any leaf field without an `evidence` tag is a process violation. Halt and re-prompt rather than emit. This is the load-bearing discipline against `brownfield laundering`.

### 4. Reviewer pass

Run `02-amazon-writing-linter` over every free-text field — tenet statements, goal statements, mechanism descriptions, dissent items. Apply the linter's revisions before emitting. Vague claims ("we focus on quality") get rejected by the linter or pushed to `assumption`.

### 5. Emit

Write the manifest at `manifest_path`. Set:

- `schema_version: 1`
- `bet.origin: brownfield`
- `bet.bootstrapped_at: <ISO-8601 now>`
- `bet.bootstrapped_by: <operator_handle>`
- `history: [<bootstrap-entry>]` where the bootstrap entry records `routing_decision: advance` and `handoff_status: proposed`, with `recommended_skill: 14-lifecycle-navigator`.

Validate the written file against `schema/governance.schema.json` before declaring success.

### 6. Handoff

Print to the operator:

```text
Manifest written to <manifest_path>.
Fields populated: N (fact: X, inference: Y, assumption: Z, open_question: W).
Next: run skill 14-lifecycle-navigator to see the next required action.
```

Do not invoke the navigator from this skill. The operator's next session — or their next invocation — is when navigation runs.

## Hard rules (non-negotiable)

```text
No manifest field without an evidence tag.
No evidence: fact without a non-null source.
No silent inference of customer/product/tenet values from README prose.
No overwrite of an existing manifest without reimport: true.
Partial mode skips are recorded as open_question, never omitted.
```

The temptation to be "helpful" by inferring fields from existing prose is the brownfield-laundering vector. This skill is helpful by refusing.

## Output schema

The skill's output IS the `governance.yaml` manifest, conforming to [`schema/governance.schema.json`](../../schema/governance.schema.json). See the populated example at [`examples/example-bootstrap.yaml`](examples/example-bootstrap.yaml).

In addition, the skill emits a one-shot summary to the operator console (counts of tagged fields, path written, next step). This summary is not persisted as a separate artifact.

## Failure modes

### brownfield laundering *(informal)*

The lifted manifest's surface signal — every field populated, schema valid, downstream skills runnable — hides the structural failure that the populated state never passed any governance gate. Downstream skills treat lifted assumptions as if they were the output of the constructive skills that should have produced them. Mitigation: every field carries an evidence tag; `fact` requires a source; the navigator's `phase laundering` second-axis check then refuses to route to interrogative skills whose required inputs are `assumption`-tagged. See [`GLOSSARY.md#brownfield-laundering`](../../GLOSSARY.md#brownfield-laundering).

### Bootstrap-quiz failure

The interview becomes a quiz the operator cannot complete in one sitting and abandons. Mitigation: support `mode: partial` — populate what's evidenced, mark unknown field groups as `open_question` collectively, only refuse on gaps that would block the *next* skill the operator wants to run. Partial manifests are valid manifests; they just constrain which downstream skills the navigator will recommend.

### Over-claim on `fact` tags

The operator claims `evidence: fact` for a value with a weak or non-resolving source. Mitigation: the `fact_requires_source` schema rule enforces source presence; the linter pass over source URLs/paths catches obviously broken links; the navigator's `phase laundering` second-axis check is the last line of defense if the source resolves but does not actually support the claim.

## Stop conditions

The skill refuses to emit output when:

- The operator asks it to "just fill in reasonable defaults" or "guess what the tenets probably are" or "infer the metrics from the code." That request is brownfield laundering by another name. Refuse and re-prompt.
- A field cannot be tagged (the operator does not know AND does not want it marked `open_question`). Refuse — `open_question` is the honest tag.
- The schema validation fails after population. Surface the error; do not write a half-valid manifest.

## Handoffs

| Output field | Consumed by |
|---|---|
| `governance.yaml` (entire manifest) | `14-lifecycle-navigator` (every invocation) |
| `bet.prfaq_path` (when null) | `14-lifecycle-navigator` recommends `01-working-backwards-prfaq` or `08-customer-interview-synthesis` next |
| `tenets[]` (when empty) | `14-lifecycle-navigator` recommends authoring tenets before `10-tenets-review` is invokable |
| `success_metrics[]` | `04-mechanism-designer`, `05-weekly-business-review`, `10-tenets-review` |
| `interviews[]` | `08-customer-interview-synthesis` |
| `period_goals[]` + `prior_gradings[]` | `11-ambitious-goal-grading` |
| `dissent_log[]` | `12-dissent-before-commit` |

The manifest is the contract. Every downstream skill reads from it; no skill writes to it except via its declared field-owners (this skill on bootstrap; the navigator on `history[]`; future skill revisions on their respective field groups).

## Optional observability emission

If the localhost observability stack at [`tools/observability/`](../../tools/observability/README.md) is running, this skill may emit events at the start and end of each field group's interview so the operator can watch the bootstrap progress in real time. Emission is best-effort: when `AMAZONIAN_OBSERVABILITY_URL` is unset or the server is down, the helper is a silent no-op. The skill must complete the bootstrap whether observability is up or not.

```bash
source scripts/lib/emit-event.sh

amazonian_emit_event 00-repo-state-import start
# ... walk the operator through field groups ...
echo '{"declined_groups":["dissent_log"]}' \
  | amazonian_emit_event 00-repo-state-import end "" "" ""
```

See [`tools/observability/README.md`](../../tools/observability/README.md) for the event schema and architectural commitments.

## Influences

- Manifest-driven import is a known pattern from infrastructure-as-code (Terraform `import`, Kubernetes resource manifests). This skill borrows the discipline that *importing existing state must be explicit and audit-trailed*, not implicit.
- The evidence-tag-on-every-field discipline is suite-original, drawn from `assumption_tags` in [`vocabulary.yaml`](../../vocabulary.yaml) and applied here as a structural constraint.
