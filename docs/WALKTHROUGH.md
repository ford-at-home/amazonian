# Amazonian: an operator walkthrough

A 15-minute path from `git clone` to a running governance session, with optional real-time observability.

This is the document to read when you've found this repo and are trying to figure out **what to do with it**. The [`README.md`](../README.md) explains *what the suite is*; this file explains *how to put it to work*.

---

## TL;DR

```bash
# 1. Clone the suite (one-time, anywhere)
git clone https://github.com/ford-at-home/amazonian.git ~/amazonian

# 2. Deploy it onto YOUR product repo
cd /path/to/your/product/repo
~/amazonian/scripts/install.sh

# 3. In Claude / Cursor, in your product repo, say:
#    "Use the repo-state-import skill to bootstrap governance.yaml."
#    Then:
#    "Use the lifecycle-navigator skill to recommend the next step."

# 4. (Optional) Watch the agent work in real time
cd ~/amazonian/tools/observability
make up-bg                    # http://127.0.0.1:8765/
```

The rest of this document explains what each step does and what to expect.

---

## Step 0 — prerequisites

- `git`, `bash` (4+), `python3` (3.10+).
- An AI coding agent that loads Cursor / Claude Code-style skills from the working directory. The suite has been validated against Cursor and Claude Code.
- A product repo you want to govern. Greenfield works; brownfield works better — that's what `00-repo-state-import` is for.

No Docker, no Node, no remote services. Everything runs locally.

## Step 1 — orient (5 minutes)

Before you deploy onto your own repo, skim two files in *this* repo so you know what you're agreeing to:

| File | Why read it | Time |
|---|---|---|
| [`README.md`](../README.md) | Top-level mental model + skill table | 3 min |
| [`LIFECYCLE.md`](../LIFECYCLE.md) | Phase model and which phases the suite deliberately doesn't cover (notably: Build) | 2 min |

You can stop there. Each individual `SKILL.md` is dense and only worth reading when you actually need that skill.

**Mental model in one paragraph:** Amazonian is a governance layer wrapped around a product development lifecycle. There are 15 skills. Some are *constructive* (they produce artifacts: a PRFAQ, a mechanism spec, a WBR). Some are *interrogative* (they review or route: leadership-principles-reviewer, dissent-before-commit, lifecycle-navigator). All skills read from and write to one file in your repo's root: `governance.yaml`. That file is the single source of truth.

## Step 2 — deploy onto your repo

```bash
cd /path/to/your/product/repo
~/amazonian/scripts/install.sh
```

What `install.sh` does:

1. Verifies you're at the root of a git repo (refuses otherwise).
2. Detects which AI client you're using by looking for `.cursor/` or `.claude/` directories. If neither, asks which to target.
3. Copies the suite's skills into the client's plugin location (e.g., `.cursor/plugins/amazonian/skills/`).
4. Detects whether the [`superpowers`](https://github.com/anthropic/superpowers) plugin is also installed. If yes, `14-lifecycle-navigator` will delegate question-driven UX to `superpowers:brainstorming`. If no, the navigator handles questioning natively.
5. Scaffolds a starter `governance.yaml` at your repo root from [`scripts/templates/governance-template.yaml`](../scripts/templates/governance-template.yaml). The starter is **schema-invalid by design** (the `bet.id` field is unset); `00-repo-state-import` fills it in.

**Idempotency:** Safe to re-run. The script refuses to overwrite an existing populated `governance.yaml`.

**Expected output:** A run log ending with `installed: <N> skills`, a path to the scaffolded manifest, and a `superpowers status: present|absent` line.

If something goes wrong, the script exits with a non-zero code and a specific diagnostic. There are no silent fallbacks.

## Step 3 — bootstrap your repo's current state

In your AI client, while in your product repo, say:

> Use the `repo-state-import` skill to bootstrap `governance.yaml`.

What the skill does: walks you through a structured interview covering tenets, success metrics, live operational mechanisms, period goals, prior interviews, and dissent history. Every field you populate gets an evidence tag:

- `fact` — written down somewhere (the skill will ask for the source path)
- `inference` — derived from something written
- `assumption` — stated but undocumented
- `open_question` — known unknown

**You cannot mark a field `fact` without giving the skill a real `source`.** That refusal is the entire point — it's why the manifest is trustworthy downstream.

The interview is decomposable: skip any field group you don't have material for. Skipped groups remain absent from the manifest (not blank), which is itself a signal.

**Expected output:** A populated `governance.yaml` in your repo root, with evidence tags on every field, plus a `history[]` entry recording when and how it was bootstrapped.

**Named risk to know about:** `brownfield laundering` — a populated manifest read by downstream skills as if it had passed governance gates when it actually never did. The evidence-tag discipline is the structural defense; if you find yourself wanting to mark something `fact` without a source, that's the risk firing.

## Step 4 — ask the navigator what to do next

> Use the `lifecycle-navigator` skill to recommend the next step.

What the skill does: reads `governance.yaml`, walks a deterministic state machine ([`skills/14-lifecycle-navigator/state-machine.yaml`](../skills/14-lifecycle-navigator/state-machine.yaml)), matches your current state to a position, and returns one of:

- `advance` — proceed to the recommended next skill
- `upstream_remediation` — the obvious next skill *would* run, but it would consume `assumption`-tagged inputs. Recommends the upstream producing skill instead, so the input becomes `fact` first.
- `block` — something irreversible would happen against `assumption`-tagged inputs (typical: `dissent-before-commit` on a hard-to-reverse decision). Stops.

**Named failure mode the navigator catches:** `phase laundering` — running a downstream skill against weak inputs and treating its output as authoritative. The check fires when any required input field is tagged `assumption` or `open_question`.

**Expected output:** A routing recommendation with the next skill named, the inputs already prepared for it, and a rationale. A `history[]` entry gets appended to `governance.yaml`.

If `superpowers` is installed, the navigator will hand off to `superpowers:brainstorming` for the question-driven part; otherwise it asks the questions itself. See [`skills/14-lifecycle-navigator/delegation-contract.md`](../skills/14-lifecycle-navigator/delegation-contract.md) for the handoff details.

## Step 5 — act on the recommendation

The navigator points you at one specific skill. Invoke it the same way:

> Use the `<skill-name>` skill.

Then loop back to step 4. The navigator's job is to keep you on the right next thing, not to do the work itself.

Common first-session paths:

| If your manifest shows… | The navigator typically routes you to… |
|---|---|
| No PRFAQ yet | `01-working-backwards-prfaq` |
| PRFAQ exists but lints poorly | `02-amazon-writing-linter` then `07-leadership-principles-reviewer` |
| Mechanisms tagged `assumption` | `04-mechanism-designer` |
| WBR due (last entry > 7 days old) | `05-weekly-business-review` |
| Period boundary hit (quarter end, etc.) | `11-ambitious-goal-grading`, then `10-tenets-review`, then `13-portfolio-review` |
| Irreversible action about to fire | `12-dissent-before-commit` |
| Incident just happened | `06-correction-of-errors` |

## Step 6 — (optional) watch the agent work in real time

The suite ships an optional localhost-only observability stack. When it's running, you can see snapshots of `governance.yaml`, events emitted by skills, and the suite's data-flow topology in a browser.

```bash
cd ~/amazonian/tools/observability
make up-bg                                          # starts server in background
open http://127.0.0.1:8765/                         # three tabs: Timeline, Topology, Manifest
```

To see what a realistic session looks like *before* you run your own:

```bash
./scripts/seed-demo.sh                              # paced walkthrough (~8 seconds)
./scripts/seed-demo.sh --fast                       # instant
```

The seed plays a worked ChangeLens session: bootstrap → navigator detects a phase-laundering risk on the WBR mechanism → recommends `04-mechanism-designer` → operator writes the spec → manifest's evidence tag flips from `assumption` (yellow border) to `fact` (green border). When done:

```bash
./scripts/teardown-demo.sh                          # clean the demo manifest + DB
make down                                           # stop the server
```

**Architectural commitment:** the observability stack is strictly optional. The skill suite works identically whether the server is up or down. `governance.yaml` is the source of truth; this stack is a projection plus an event log. See [RFC-002 §3](rfcs/RFC-002-localhost-observability.md) for why this distinction matters.

---

## Where to go from here

| Goal | Read |
|---|---|
| Understand the deployment design | [`docs/rfcs/RFC-001-deployment-and-orchestration.md`](rfcs/RFC-001-deployment-and-orchestration.md) |
| Understand the observability design | [`docs/rfcs/RFC-002-localhost-observability.md`](rfcs/RFC-002-localhost-observability.md) |
| Understand a specific skill | The corresponding `skills/<NN>-<name>/SKILL.md` |
| Understand the suite's design language (named failure modes, evidence tags, etc.) | [`GLOSSARY.md`](../GLOSSARY.md) |
| Understand how to author a new skill | [`SKILL_DESIGN_PATTERN.md`](../SKILL_DESIGN_PATTERN.md) |
| See what the manifest schema actually permits | [`schema/governance.schema.json`](../schema/governance.schema.json) |
| Look up canonical enums (evidence tags, decision recommendations, etc.) | [`vocabulary.yaml`](../vocabulary.yaml) |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `install.sh` says "not a git repo" | Ran outside a git checkout | `cd` to your product repo root and re-run |
| `install.sh` says "governance.yaml exists" | Re-running on a repo that already has the suite | Either you're done, or you want to re-bootstrap — delete `governance.yaml` first if you really want a clean start |
| `00-repo-state-import` refuses to mark something `fact` | You didn't provide a `source` | Find the actual source, or drop the evidence to `assumption` honestly |
| `14-lifecycle-navigator` keeps returning `upstream_remediation` | Your manifest has too many `assumption`-tagged required inputs | That's the suite working as designed — the navigator is refusing to launder weak inputs through downstream skills. Address them upstream first. |
| `make up-bg` says "address already in use" | Another service on port 8765 | `make up-bg PORT=9000` (or stop the conflicting service) |
| Observability tab "Timeline" is empty after editing `governance.yaml` | The server isn't watching your repo's `governance.yaml`, only this suite's | Set `AMAZONIAN_OBS_MANIFEST_PATH=/path/to/your/repo/governance.yaml` and restart the server |
| `seed-demo.sh` says "observability not reachable" | Server isn't running, or running on a non-default port | `make up-bg` first; pass `AMAZONIAN_OBSERVABILITY_URL=http://127.0.0.1:9000` if you changed the port |
