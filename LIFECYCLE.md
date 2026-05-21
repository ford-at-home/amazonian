# Skill Lifecycle

This suite is **not a product development lifecycle (PDLC)**. It is the **governance layer around one**.

> Machine-readable companion: [`lifecycle.yaml`](lifecycle.yaml). Agents can query phase coverage, skill categories, required reviews, and skill-level handoffs without parsing this document.

The suite's job is to make sure what enters Build is contracted (PRFAQ / six-pager passed the gates), and what leaves Build is inspectable (mechanism + WBR + CoE) and falsifiable (tenets-review). Build itself happens in engineering tools you already have. Pretending a skill suite is a sprint board is how skill suites die.

## Phase coverage

| Phase | What happens | Skills | Density |
|-------|--------------|--------|---------|
| **Discover** | Hunt for problems, customer signal, opportunity sizing | `customer-interview-synthesis` | partial |
| **Define** | Specify what / for whom / why | `working-backwards-prfaq`, `six-page-narrative`, `amazon-writing-linter`†, `leadership-principles-reviewer`† | dense |
| **Design** | Architecture, UX, operational mechanism | `mechanism-designer` (operational), `six-page-narrative` (strategic) | partial |
| **Build** | Implementation | — | empty (deliberate) |
| **Launch** | Release gating | `launch-readiness-review` | partial |
| **Operate** | Run, inspect, escalate | `mechanism-designer`, `weekly-business-review` | dense |
| **Learn** | Incident review, thesis re-examination | `correction-of-errors` (incident-driven), `tenets-review` (event-driven) | partial |

† Cross-cutting reviewer passes; not phase-bound.

## Deliberate omissions

- **Build phase.** Implementation happens in engineering tooling (Jira, Linear, CI/CD, feature flags). No skill in this suite manages sprints, branches, or deploys.
- **Launch operations.** `launch-readiness-review` *gates* the launch; it does not orchestrate it. Release engineering — deploys, rollouts, canaries — is engineering's domain.
- **Roadmap planning.** No portfolio-prioritization skill. The PRFAQ packet and tenets-review provide inputs to a portfolio decision; they do not make it.

These omissions are the boundary. The suite is the *bookends*. Whether you fill the middle with engineering rigor is up to you and out of scope here.

## Constructive vs interrogative

The suite splits roughly 50/50 by epistemic posture:

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
- `tenets-review` — stress-tests whether the original thesis is still worth pursuing

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
3. **Design** — `mechanism-designer` defines the operating cadence that will keep the bet honest after launch.
4. **Build** — happens in your engineering process. The suite is silent here on purpose.
5. **Launch** — `launch-readiness-review` gates the ship decision by diffing the build against the PRFAQ contract.
6. **Operate** — `weekly-business-review` inspects the metrics on cadence; `correction-of-errors` fires on incidents.
7. **Learn** — `tenets-review` fires on external context shifts or annually; recommends continue / kill / pivot / escalate.

The chain is not strict. PRFAQs can run without interview synthesis (you accept the assumption tags). Six-pagers can run without a prior PRFAQ. Launch-readiness can run on an artifact whose PRFAQ has drifted (that drift is the point). What matters is that each artifact is contracted and inspectable.

## Where this leaves you

The suite handles **the entrance** (Discover/Define) and **the exit** (Operate/Learn) of any significant bet. Build and most of Launch happen elsewhere. The suite's value is not in covering every phase — it is in making the bookends load-bearing enough that the middle has somewhere honest to attach.

Pick the skills relevant to where you are in the lifecycle. Don't invoke them all on every project.
