# Skill Lifecycle

This suite is **not a product development lifecycle (PDLC)**. It is the **governance layer around one**.

> Machine-readable companion: [`lifecycle.yaml`](lifecycle.yaml). Agents can query phase coverage, skill categories, required reviews, and skill-level handoffs without parsing this document.

The suite's job is to make sure what enters Build is contracted (PRFAQ / six-pager passed the gates), and what leaves Build is inspectable (mechanism + WBR + CoE) and falsifiable (tenets-review). Build itself happens in engineering tools you already have. Pretending a skill suite is a sprint board is how skill suites die.

## Phase coverage

| Phase | What happens | Skills | Density |
|-------|--------------|--------|---------|
| **Deploy** | Bring an existing repo into the suite's contracted state | `repo-state-import` | dense |
| **Discover** | Hunt for problems, customer signal, opportunity sizing | `customer-interview-synthesis` | partial |
| **Define** | Specify what / for whom / why | `working-backwards-prfaq`, `six-page-narrative`, `amazon-writing-linter`†, `leadership-principles-reviewer`† | dense |
| **Design** | Architecture, UX, operational mechanism, pre-execution gating | `mechanism-designer` (operational), `six-page-narrative` (strategic), `dissent-before-commit` (pre-execution gate) | partial |
| **Build** | Implementation | — | empty (deliberate) |
| **Launch** | Release gating | `launch-readiness-review` | partial |
| **Operate** | Run, inspect, escalate | `mechanism-designer`, `weekly-business-review` | dense |
| **Learn** | Incident review, thesis re-examination, goal calibration, cross-bet allocation | `correction-of-errors` (incident-driven), `tenets-review` (event-driven), `ambitious-goal-grading` (period-driven), `portfolio-review` (period-driven, cross-bet) | dense |
| *Cross-cutting* | Question-driven routing across phases | `lifecycle-navigator`† | per-session |

† Cross-cutting passes; not phase-bound. `lifecycle-navigator` is read-mostly (it reads `governance.yaml` and emits routing recommendations); `amazon-writing-linter` and `leadership-principles-reviewer` are draft-review passes any authoring skill runs against its output.

## Deliberate omissions

- **Build phase.** Implementation happens in engineering tooling (Jira, Linear, CI/CD, feature flags). No skill in this suite manages sprints, branches, or deploys.
- **Launch operations.** `launch-readiness-review` *gates* the launch; it does not orchestrate it. Release engineering — deploys, rollouts, canaries — is engineering's domain.
- **Roadmap planning at the proposal level.** No skill in this suite generates the initial list of candidate bets. `customer-interview-synthesis` surfaces what customers are signaling; `portfolio-review` allocates capacity across already-proposed bets; neither invents the proposal set.

These omissions are the boundary. The suite is the *bookends*. Whether you fill the middle with engineering rigor is up to you and out of scope here.

### Rejected skill categories

Beyond the phase-level omissions above, the suite has explicitly rejected several proposed skill categories during design review. Documenting them here so future contributors do not re-propose them without addressing the original objection:

| Category | Why rejected |
|---|---|
| Circuit Breaker Orchestration | Execution-layer. The suite has no business deciding *at runtime* whether to halt a workflow; that belongs in the engineering systems that actually run the workflow. |
| Rotational Subagent Allocation | Execution-layer. Routing decisions between agents at runtime are not a governance artifact; they are a runtime concern. |
| Shadow Pipeline | Execution-layer. Same reasoning. |
| Hierarchical Goal Decomposition | The constructive parts already exist (`working-backwards-prfaq` decomposes via `success_metrics`; `mechanism-designer` decomposes via `inputs` → `inspection`). The interrogative part is now covered by `ambitious-goal-grading`. A combined skill would have collapsed two distinct phases and two distinct epistemic postures. |

The disqualifying rule each violates: a proposed skill must satisfy the spine in [`SKILL_DESIGN_PATTERN.md`](SKILL_DESIGN_PATTERN.md), produce an artifact a downstream skill consumes, and avoid collapsing constructive and interrogative responsibilities into a single skill. Execution-layer routing fails the first; multi-mode skills fail the third.

## Constructive vs interrogative

The suite has 13 skills — 5 constructive, 8 interrogative — split by epistemic posture:

**Constructive** (produce an artifact):

- `working-backwards-prfaq`
- `six-page-narrative`
- `mechanism-designer`
- `weekly-business-review`
- `correction-of-errors`

**Interrogative** (stress-test an artifact or belief; produce revisions, not new artifacts):

- `customer-interview-synthesis` — stress-tests the founder's prior on the customer
- `amazon-writing-linter` — stress-tests prose for evidence and decision relevance
- `leadership-principles-reviewer` — stress-tests proposals against principles
- `launch-readiness-review` — stress-tests build state vs PRFAQ contract
- `tenets-review` — stress-tests whether one bet's original thesis is still worth pursuing
- `ambitious-goal-grading` — stress-tests whether one bet's targets were set at honest difficulty, independent of outcome
- `dissent-before-commit` — stress-tests whether the strongest current case against firing a specific action has been addressed or accepted, not just acknowledged
- `portfolio-review` — stress-tests whether the allocation **across** all current bets is coherent given current information, via zero-based reallocation

Interrogative skills are the falsification layer. They produce no artifact of their own — they produce *revisions* to the artifacts other skills emit.

Users will be tempted to invoke them confirmatorily. Every interrogative skill must refuse that posture explicitly in its stop conditions. A reviewer asked to "confirm this is good" is being asked to fail at its job.

## Required reviews

Authoring skills declare `required_reviews` in their frontmatter. The artifact is not considered complete until those reviewers have run and their revisions have been incorporated. This converts the soft promise "if a reviewer is available, hand it the prose" into a contract.

| Authoring skill | Required reviews |
|---|---|
| `working-backwards-prfaq` | `amazon-writing-linter`, `leadership-principles-reviewer` |
| `six-page-narrative` | `amazon-writing-linter`, `leadership-principles-reviewer` |
| `mechanism-designer` | `amazon-writing-linter` |
| `correction-of-errors` | `amazon-writing-linter` |
| `weekly-business-review` | — *(cadence-driven; reviewer friction harms weekly rhythm)* |

Reviewer skills do not declare `required_reviews`. They are leaves.

## Sequencing in practice

A typical bet runs through the suite roughly like this:

1. **Discover** — `customer-interview-synthesis` turns raw interview signal into PRFAQ-ready structured inputs with evidence tags.
2. **Define** — `working-backwards-prfaq` consumes those inputs; required-reviews run; six-pager added when architectural depth needed.
3. **Design** — `mechanism-designer` defines the operating cadence that will keep the bet honest after launch. Before any mechanism fires (or any irreversible action executes), `dissent-before-commit` surfaces the strongest current case against execution and forces it to be addressed or accepted with a named tradeoff — not just acknowledged.
4. **Build** — happens in your engineering process. The suite is silent here on purpose.
5. **Launch** — `launch-readiness-review` gates the ship decision by diffing the build against the PRFAQ contract.
6. **Operate** — `weekly-business-review` inspects the metrics on cadence; `correction-of-errors` fires on incidents.
7. **Learn** — four skills, four questions:
   - `correction-of-errors` (incident-driven): *what broke?*
   - `tenets-review` (event-driven, per-bet): *was the bet right?*
   - `ambitious-goal-grading` (period-driven, per-bet): *were the targets set at honest difficulty?*
   - `portfolio-review` (period-driven, cross-bet): *is the allocation across all bets coherent?*

   These are deliberately separate. A team can pass three and fail the fourth — for example, individual bets each pass their per-bet checks while the collective portfolio drifts into incoherent marginal allocation. Each LEARN skill catches a failure mode the others miss. The per-bet skills feed `portfolio-review`; `portfolio-review` does not replace them.

The chain is not strict. PRFAQs can run without interview synthesis (you accept the assumption tags). Six-pagers can run without a prior PRFAQ. Launch-readiness can run on an artifact whose PRFAQ has drifted (that drift is the point). What matters is that each artifact is contracted and inspectable.

## Where this leaves you

The suite handles **the entrance** (Discover/Define) and **the exit** (Operate/Learn) of any significant bet. Build and most of Launch happen elsewhere. The suite's value is not in covering every phase — it is in making the bookends load-bearing enough that the middle has somewhere honest to attach.

Pick the skills relevant to where you are in the lifecycle. Don't invoke them all on every project.
