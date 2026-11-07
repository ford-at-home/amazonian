# Six-Page Narrative — <title>

> Decision memo. Prose, not slides. Tag every empirical claim with `[fact]`, `[assumption]`, `[inference]`, or `[open question]`.

---

## 1. Context

<2–4 paragraphs. What the reader needs to know to evaluate this proposal. Recent history, organizational state, market shift, prior decisions. Past tense for what happened; present tense for what is true now.>

## 2. Customer / User Problem

<2–3 paragraphs. The specific customer or user, the specific problem, the specific cost of not solving it. Cite evidence. Distinguish problem from symptom.>

## 3. Current State

<2–3 paragraphs. What exists today, including how it fails. Be specific about failure modes; quote real numbers where available. This section is a contract: if the current state is misrepresented, the rest of the memo is invalid.>

## 4. Proposed Mechanism

<3–4 paragraphs. The proposed change. Concrete enough that a reader can imagine implementation. Specify: cadence, inputs, outputs, ownership, escalation. If recurring, this section should hand off to `mechanism-designer` for the operational specification.>

## 5. Alternatives Considered

<For each alternative, one paragraph: what it was, why it was rejected. At least two real alternatives. Steel-man each before dismissing.>

### Alternative A: <name>

<What it was, who proposed it, why it was rejected — with reasoning a reviewer can verify.>

### Alternative B: <name>

<…>

## 6. Risks and Mitigations

| Risk | Severity (1–5) | Likelihood (1–5) | Mitigation | Owner |
|------|----------------|------------------|------------|-------|
|      |                |                  |            |       |

<Each risk needs a specific mitigation. "We will monitor" is not a mitigation.>

## 7. Metrics

| Metric | Baseline | Target | How measured | Time to evaluate |
|--------|----------|--------|--------------|------------------|
|        |          |        |              |                  |

<Distinguish input metrics (controllable) from output metrics (lagging). Specify what failure looks like, not just success.>

## 8. Dissent

<Named individuals who disagreed with this proposal and their stated position. If no dissent was found, state explicitly that you sought it and from whom.>

| Dissenter | Position | Author's response |
|-----------|----------|-------------------|
|           |          |                   |

> "I have not had a single conversation with someone who disagrees" is a dissent failure, not a dissent absence.

## 9. Decision Needed

<One paragraph. The specific decision the reader is being asked to make.>

**Recommendation:** <a single sentence>

**Decision needed by:** <date>

**Decision-maker:** <name>

## 10. Appendix

### Assumptions register

| # | Assumption | Evidence (or lack thereof) | Risk if wrong |
|---|------------|----------------------------|---------------|
| 1 |            |                            |               |

### Supporting data

<Charts, tables, prior memos, customer interviews. Linked, not pasted, unless central to the argument.>

### Prior art

<What this builds on. What it replaces. What it deprecates.>
