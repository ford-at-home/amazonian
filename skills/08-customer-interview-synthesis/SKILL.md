---
name: customer-interview-synthesis
description: Convert raw customer interview transcripts, notes, and surveys into PRFAQ-ready structured inputs — customer segments, problem statement, current workarounds, evidence tags, and founder-bias flags. Distinguishes behavioral evidence from attitudinal evidence and refuses to synthesize PRFAQ-ready output from fewer than 8 interviews. Use when raw customer signal exists but is unstructured, before drafting a PRFAQ; or when the user mentions "interview synthesis", "user research", "discovery synthesis", "interview themes", or "customer signal".
category: interrogative
---

# Customer Interview Synthesis

Convert unstructured customer interview signal into PRFAQ-ready structured inputs. Distinguishes what respondents *did* (behavioral) from what they *said they'd do* (attitudinal). Refuses to synthesize PRFAQ-grade conclusions from a panel that is too small, too friendly, or too leading. Surfaces founder bias as a first-class output.

This skill is interrogative. It produces *inputs to the PRFAQ*, not a PRFAQ. If asked to "confirm the product idea is validated," it refuses.

## Quick start

1. Collect the inputs below. Distinguish transcripts from interviewer notes — they are not the same evidence.
2. Run the validation gates *before* synthesizing. Minimum N is enforced; below the floor, the skill emits `target_artifact: exploratory` only.
3. Cluster segments. Tag every claim by evidence type (behavioral / attitudinal) and assumption tag (`[fact]` / `[assumption]` / `[inference]` / `[open question]`).
4. Hunt for founder bias and selection bias against [`bias-patterns.yaml`](bias-patterns.yaml). Strip any flag that lacks a quoted citation.
5. Emit the structured packet, including an explicit `prfaq_input_map` from this output to the PRFAQ's input fields.

## When to use

- Raw interview signal exists (transcripts, notes, survey responses) and a PRFAQ is the next artifact.
- A PRFAQ draft was attempted and failed the "specific customer" or "workaround documented" gates.
- The user mentions: "interview synthesis", "user research synthesis", "discovery themes", "customer signal", "research debrief".

## When NOT to use

- No interviews have been conducted. Conduct them first; this skill does not invent customers.
- The artifact needed is a market analysis or competitive teardown. Different skill set.
- The user wants reassurance that the idea is validated. This skill is designed to find disconfirming evidence; it will be unsatisfying.

## Inputs

```yaml
hypothesis_going_in:            # what the founder believed before interviews; required for bias-flag detection
target_artifact:                # prfaq | six_pager | exploratory
transcripts:                    # list of verbatim transcripts (weighted high)
structured_notes:               # list of interviewer notes (weighted low; carry interviewer bias)
survey_responses:               # optional structured survey data (weighted medium)
interview_count:                # integer — total N across all artifact types
selection_method:               # how respondents were chosen: cold outreach, friend-of-friend, existing customers, panel, etc.
interview_method:               # how interviews were conducted: open-ended, scripted, semi-structured; who conducted them
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Minimum N for PRFAQ | `interview_count >= 8` if `target_artifact == prfaq` or `six_pager` | Drop `target_artifact` to `exploratory` and emit with `prfaq_ready: false` |
| Transcripts vs notes distinguished | Inputs separate `transcripts` from `structured_notes`; behavioral evidence cites transcripts | Re-request inputs |
| Citation for every behavioral claim | Each `behavioral_evidence` entry has a quoted phrase from a named transcript | Strip the claim or relabel as `attitudinal` |
| Citation for every bias flag | Each `bias_flags` entry has a quoted phrase from `selection_method`, `interview_method`, or a transcript | Strip the flag |
| Frequency is numeric | Every `current_workarounds[].frequency` has `{count, of_n}` | Replace prose ("common", "several") with numbers or strip |
| Assumption-tag vocabulary | Every claim uses `[fact]` / `[assumption]` / `[inference]` / `[open question]` — no parallel system | Re-tag |
| Attitudinal-only flagged | Any segment whose evidence is 100% attitudinal carries `evidence_basis: [assumption]` and a warning | Add the warning |

## Process

1. **Collect** transcripts, notes, surveys. Keep them separately tagged — do not merge.
2. **Gate-check.** If `interview_count < 8`, force `target_artifact: exploratory` before proceeding.
3. **Affinity-cluster** quotes into candidate segments. Each cluster carries the source transcript_id for every quote.
4. **Classify** each piece of evidence per segment as `behavioral` or `attitudinal` per [`GLOSSARY.md`](../../GLOSSARY.md#evidence-type).
5. **Tag** every claim with an assumption tag. A segment with only attitudinal evidence cannot be tagged `[fact]`.
6. **Quantify workarounds** with `frequency: {count, of_n}`. Strip workarounds that no respondent mentioned.
7. **Hunt for bias** against [`bias-patterns.yaml`](bias-patterns.yaml). For each pattern matched, attach the quoted citation. If you cannot quote a source, the flag does not exist.
8. **Map to PRFAQ inputs** explicitly in `prfaq_input_map`. The mapping must name which segment becomes the PRFAQ `customer`, which problem statement, which workaround.
9. **Set `prfaq_ready`** only if all gates pass and the gates produced at least one segment with behavioral corroboration.

## Hard rule (non-negotiable)

```text
No bias flag without a quoted citation.
No PRFAQ-ready output from fewer than 8 interviews.
A segment with zero behavioral evidence is tagged [assumption], never [fact].
```

LLM-driven bias hunting will hallucinate plausible-sounding patterns when uncertain. The citation requirement is the only thing standing between this skill and bias-flag theater.

## Output schema

```yaml
target_artifact:                # prfaq | six_pager | exploratory
interview_count:
weighted_n:                     # transcripts*1.0 + survey*0.5 + notes*0.25 — informational
customer_segments:
  - segment_label:
    n_supporting:               # integer — respondents whose evidence supports this segment
    evidence_basis:             # [fact] | [assumption] | [inference] | [open question]
    behavioral_evidence:
      - claim:
        citation:               # quoted phrase
        transcript_id:
    attitudinal_evidence:
      - claim:
        citation:
        transcript_id:
    conflict_with_segments:     # which other segments and why — segment heterogeneity is information
customer_problem:
  stated:                       # what respondents said the problem is
  stated_citations:             # quotes
  inferred_underlying:          # what the synthesist infers; tagged [inference] only
  basis:                        # quoted citations supporting the inference
current_workarounds:
  - workaround:
    frequency:
      count:                    # integer
      of_n:                     # integer denominator
    switching_cost_signal:      # what evidence suggests the cost of switching from this workaround
    citation:
assumption_flags:
  - assumption:
    tag:                        # [assumption] | [open question]
    basis:
    recommended_action:         # how to convert to [fact] — what evidence would resolve it
bias_flags:                     # NEVER emitted without a citation
  - pattern:                    # which pattern from bias-patterns.yaml
    citation:                   # quoted from selection_method, interview_method, or a transcript
    risk:                       # what this bias does to the conclusions
founder_hypothesis_status:
  original: <copy of hypothesis_going_in>
  supported_by_evidence:        # bool — strictly per evidence, not vibes
  evidence_for:
  evidence_against:             # required — if empty, that itself is a bias flag
prfaq_ready:                    # bool — true only if all gates pass and at least one segment has behavioral corroboration
prfaq_blockers:                 # if not ready, what's missing
prfaq_input_map:                # explicit field-level handoff to working-backwards-prfaq
  customer:                     # which segment becomes the PRFAQ `customer`
  customer_problem:             # which problem statement
  current_workaround:           # which workaround
  desired_customer_outcome:     # inferred or directly stated; cite source
  known_evidence:               # which behavioral evidence transfers
  unknowns:                     # which open questions become PRFAQ `unknowns`
```

## Stop conditions

Stop and ask the user. Do not invent.

- `interview_count == 0`.
- Transcripts are summaries written by the founder rather than verbatim records.
- The user requests confirmation that "the idea is validated." Refuse; offer to surface disconfirming evidence instead.
- `hypothesis_going_in` is missing. Without it, founder-bias detection cannot run honestly.
- All inputs are `structured_notes` with no transcripts and no surveys. Notes alone are interviewer-filtered; the skill will run with a heavy warning but cannot set `prfaq_ready: true`.

## Failure modes

- **Bias-flag theater.** Generating plausible-sounding bias flags without citations to back them. The citation gate is the only safeguard; do not soften it.
- **Theme washing.** Collapsing dissenting respondents into a majority theme. Segment heterogeneity is information; preserve conflicts in `conflict_with_segments`.
- **Attitudinal laundering.** Repackaging stated preference as evidence of demand. If nobody behaved, nobody validated.
- **Synthesis as confirmation.** Re-stating the founder's hypothesis back as "themes from the interviews." If `evidence_against` is empty, the synthesis is failing.
- **Friend-panel blindness.** Cohort recruited from the founder's network produces ~uniformly positive signal. The skill must call this out per [`bias-patterns.yaml`](bias-patterns.yaml) — *with citations*.
- **Note-as-transcript.** Treating an interviewer's filtered summary as if it were verbatim. The schema distinguishes them for a reason.

## Reviewer pass

After synthesizing, run a second pass that checks:

- `evidence_against` for the founder hypothesis is non-empty (or its emptiness is itself flagged).
- No bias flag lacks a citation.
- No segment claims `[fact]` without behavioral evidence.
- `prfaq_input_map` names a specific segment for the PRFAQ `customer` field — not a category.

## Follow-up mechanism

- Output feeds directly into `working-backwards-prfaq` via the `prfaq_input_map` field.
- If `prfaq_ready: false`, the `prfaq_blockers` list names the additional interviews or behavioral evidence needed.
- Bias flags should be archived with the research artifact; future synthesists need to see what the prior panel missed.

## Handoffs

**Consumes from**

- User inputs: transcripts, notes, surveys, selection and interview method, founder hypothesis.

**Feeds into**

- `working-backwards-prfaq`: `prfaq_input_map.customer` → `customer`; `prfaq_input_map.customer_problem` → `customer_problem`; `prfaq_input_map.current_workaround` → `current_workaround`; `prfaq_input_map.known_evidence` → `known_evidence`; `prfaq_input_map.unknowns` → `unknowns`
- `six-page-narrative` (when `target_artifact: six_pager`): `customer_segments` → `current_state` context; `bias_flags` → `risks`

Enums used: `evidence_type`, `interview_artifact_type`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
