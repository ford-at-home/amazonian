---
name: portfolio-review
description: Stress-test a team's collective portfolio of bets across a period. Asks not "is each bet still right?" (that is `tenets-review`) but "given everything we know now, is the allocation across all of our current bets coherent?" Emits per-bet recommendations (continue / wind_down / amplify / hold / pivot), a zero-based reallocation comparison, and an explicit drift report. The named failure mode is portfolio drift — the portfolio that exists now is the residue of accumulated past decisions, not the portfolio anyone would intentionally author today; the surface signal (stable composition, defensible per-bet stories) hides incoherent marginal allocation. Use when a period closes and cross-bet allocation is up for review; or when the user mentions "portfolio review", "OKR cycle", "bet allocation", "investment review", or "kill list".
category: interrogative
required_reviews: []
---

# Portfolio Review

A cross-bet stress test. The other Learn-phase skills are per-bet: `tenets-review` asks whether one bet's thesis is still right, `ambitious-goal-grading` asks whether one bet's goals were honestly calibrated, `correction-of-errors` asks what broke in one incident. This skill operates one layer up: given the full set of bets the team is currently running, **is the allocation across them coherent given what we know now?**

This skill is interrogative. Its second-axis check is the zero-based reallocation: if you were authoring this portfolio from scratch today with the same total capacity, would it look like the portfolio you actually have? The gap between actual and zero-based is portfolio drift.

This skill draws on a tradition that is not Amazon's. Google's OKR/portfolio-review cycle and venture-capital portfolio management both surface the cross-bet allocation question explicitly. See [`README.md`](../../README.md#influences) for the suite's full attribution.

## Quick start

1. Collect the inputs below. The skill cannot run without the prior-period outputs from `tenets-review` and `ambitious-goal-grading` for each current bet.
2. Run the validation gates *before* recommending allocations. A bet without a recent tenets-review is a bet without a defensible thesis.
3. Generate the zero-based hypothetical portfolio first — independently of the current allocation. Only then diff the actual against the hypothetical.
4. Recommend per-bet actions and per-candidate decisions. Every recommendation must cite triggering evidence.
5. If `changes_made == false`, justify the status quo against the zero-based reallocation. Status-quo defense is not free.

## When to use

- A planning cycle is closing (quarter, half, year) and cross-bet allocation is up for review.
- The team has 3+ active bets and a backlog of candidate alternatives.
- A specific candidate alternative is being considered and the question is "which current bet, if any, does it displace?"
- The user mentions: "portfolio review", "OKR cycle review", "investment review", "bet allocation", "kill list", "stack-rank our bets".

## When NOT to use

- The team is running one bet. Cross-bet allocation has no meaning at N=1. Use `tenets-review`.
- The question is about a single bet's thesis or calibration. Use `tenets-review` or `ambitious-goal-grading`.
- The question is about *how* to execute a chosen reallocation (not whether). Reallocation execution is a `mechanism-designer` problem, and any irreversible allocation action that comes out of this review should pass through `dissent-before-commit`.
- The user wants confirmation that the current portfolio is healthy. This skill is designed to detect drift; it will be unsatisfying.

## Inputs

```yaml
review_period:                  # quarter | half | year | other (named)
total_capacity:                 # team capacity in the period; integer units (people-quarters, $, ECUs — any comparable unit)
capacity_unit:                  # string: how to read the integer above
current_bets:
  - bet_id:                     # stable identifier
    name:
    prfaq_ref:                  # link or citation to the PRFAQ that authorized the bet
    phase:                      # discover | define | design | build | operate | scaling
    period_allocation:          # capacity consumed this period
    cumulative_allocation:      # capacity consumed since inception
    age_in_periods:             # how many review periods the bet has been running
    latest_tenets_review:       # REQUIRED — link to most recent tenets-review output
                                # missing this means the bet has no defensible thesis check; skill refuses to recommend
    latest_goal_grading:        # REQUIRED if the bet had period_goals; link to most recent AGG output
    cumulative_wbr_variance:    # signed aggregate of period variance from WBR
    materialized_risks:         # risks from PRFAQ that have actually materialized
candidate_alternatives:         # bets in the backlog that are NOT currently funded
  - candidate_id:
    name:
    prfaq_ref:                  # link to a PRFAQ-or-equivalent for the candidate
    estimated_capacity_need:    # in capacity_unit
    why_not_funded:             # honest reason — "no capacity" requires this skill to test that claim
    expected_return:            # the case for funding now; cite evidence, not prose
context:
  market_shifts:                # external context changes since last portfolio review
  organizational_shifts:        # team capacity changes, strategic priority shifts
  prior_kill_decisions:         # bets killed in prior periods — protects against re-funding without acknowledgment
prior_portfolio_review:         # the last portfolio-review output, if one exists
                                # if drift was named in the prior review and is still present, that is escalating evidence
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Recent tenets-review per bet | Every `current_bets[].latest_tenets_review` exists and is from within the review period or one prior | Run `tenets-review` on the missing bets first; do not proceed |
| Allocations sum to capacity | Sum of `current_bets[].period_allocation` is within 5% of `total_capacity` | Reconcile the difference (unallocated capacity is a portfolio decision; name it) |
| Candidates have PRFAQs | Every `candidate_alternatives[]` has a `prfaq_ref` | Candidates without PRFAQs cannot be honestly compared against current bets |
| Zero-based ordered first | The skill generates `zero_based_reallocation` *before* `bet_recommendations` | Re-order; the actual portfolio must not anchor the hypothetical |
| Status-quo justified explicitly | If `changes_made == false`, `status_quo_justification` is non-empty AND `zero_based_passed == true` | A no-change review without a passing zero-based check is review theater; force a change or justify |
| Kill candidate exists | At least one `bet_recommendations[]` is `wind_down` OR `pivot`, OR a documented argument that the current portfolio survives zero-based authoring | A portfolio review that produces no kills and no zero-based justification is the canonical instance of portfolio drift; reject the review |
| Candidates evaluated | Every `candidate_alternatives[]` has a `candidate_decisions[]` entry; "no decision" is not an option | Force a decision on each candidate; carrying them forever is itself portfolio drift |

## Process

1. **Collect inputs.** If any current bet lacks a recent `tenets-review`, stop. Run that first.
2. **Generate the zero-based hypothetical portfolio.** Independently of the actual allocation, decide: given the candidate set (current bets + candidate alternatives) and `total_capacity`, what would you authorize if you were starting today? Use `latest_tenets_review`, `latest_goal_grading`, `materialized_risks`, and `expected_return` to rank. Do not consult the actual allocation while generating this.
3. **Diff the actual portfolio against the zero-based portfolio.** For every gap, name the reason. "Sunk cost" and "no one wants to make the call" are valid reasons but must be named explicitly — they are the substance of portfolio drift.
4. **Match drift evidence to patterns.** Run the gaps against [`allocation-patterns.yaml`](allocation-patterns.yaml). For each pattern matched, attach the citation (which bet, which evidence).
5. **Recommend per-bet actions.** Each recommendation is one of: `continue`, `wind_down`, `amplify`, `hold`, `pivot`. Each requires a `new_allocation` and `triggering_evidence`.
6. **Decide on candidates.** For each `candidate_alternatives[]`: `fund`, `continue_to_park`, or `reject`. A `fund` decision must name `opportunity_cost_against` — which current bet's allocation it draws from. "Found capacity" requires explanation.
7. **Compose the portfolio narrative.** 3–5 sentences leadership can use that surface the kills and amplifications, not just the totals. The narrative is not optional, and it cannot launder a no-change review.
8. **Run the review-integrity check.** If `changes_made == false`, run a second internal pass that explicitly compares the actual portfolio item-by-item against the zero-based portfolio and certifies they match. If they don't match, the recommendation must change.

## Hard rule (non-negotiable)

```text
"Continue at current allocation" requires the same evidentiary burden as "kill" or "amplify".
A portfolio review that produces no allocation changes must pass a zero-based check, item-by-item.
The zero-based hypothetical is generated before the actual portfolio is consulted.
A bet with a stale tenets-review cannot be carried; run tenets-review first or wind the bet down.
A candidate alternative cannot be parked indefinitely; carrying it forever is itself drift.
```

These rules exist because portfolio reviews fail in characteristic ways: anchoring on the status quo (the actual portfolio biases the hypothetical), social cost of kills (no one wants to be the one to call the kill), and quiet candidate parking (the backlog grows but nothing moves). The rules force each failure mode to surface.

## Output schema

```yaml
review_period:
total_capacity:
capacity_unit:
zero_based_reallocation:                  # REQUIRED — the second-axis check, generated FIRST
  hypothetical_portfolio:                 # if authoring from scratch today, what would it be?
    - bet_or_candidate_id:
      allocation:
      rationale:                          # cite tenets-review, AGG, materialized_risks, expected_return
  drift_from_actual:
    - bet_id:
      current_allocation:
      zero_based_allocation:
      delta:                              # signed, in capacity_unit
      reason_for_delta:                   # "sunk cost", "social cost of kill", "no replacement ready", etc. — name it
      pattern_match:                      # from allocation-patterns.yaml, if applicable
bet_recommendations:
  - bet_id:
    recommendation:                       # continue | wind_down | amplify | hold | pivot
    new_allocation:
    rationale:
    confidence:                           # [fact] | [assumption] | [inference] | [open question]
    triggering_evidence:                  # cite tenets-review, AGG, cumulative_wbr_variance, market_shifts, etc.
    if_pivot:                             # required when recommendation == pivot
      pivot_hypothesis:
      validation_needed:
      revised_capacity:
candidate_decisions:
  - candidate_id:
    recommendation:                       # fund | continue_to_park | reject
    new_allocation:                       # in capacity_unit; required if fund
    rationale:
    opportunity_cost_against:             # which current bet's allocation gets drawn from; required if fund
                                          # required even if drawn from "unallocated capacity" — name the bet that did not get that capacity
drift_detected:
  - pattern:                              # from allocation-patterns.yaml
    affected_bets:
    evidence:                             # cited
    severity:                             # blocking | significant | acceptable
portfolio_narrative:                      # 3-5 sentences leadership can use; honest, includes kills/amplifications
review_integrity:
  changes_made:                           # bool
  total_allocation_change:                # signed; sum of |new_allocation - period_allocation| across recommendations
  zero_based_passed:                      # bool — does the resulting portfolio match the zero_based hypothetical item-by-item?
  status_quo_justification:               # required string when changes_made == false; null otherwise
                                          # "we reviewed and chose to keep everything" is NOT acceptable; specify why each bet survives zero-based
  kill_candidates_considered:             # list of bet_ids that were considered for wind_down even if not recommended for it
```

## Stop conditions

Stop and ask the user. Do not invent.

- Any `current_bets[].latest_tenets_review` is missing or older than two review periods. Run tenets-review first; do not run portfolio-review on stale thesis data.
- `total_capacity` is undefined or qualitative ("we have some capacity"). Portfolio review requires a defined budget; without it, every comparison is a vibe.
- `candidate_alternatives` is empty. A portfolio review with no candidate alternatives is a kill review — proceed but rename the artifact; the review cannot make `fund` decisions if nothing is on the table to fund.
- The user requests "validate that our current allocation is right." Refuse; offer to run the zero-based check and surface drift instead.
- The team has restructured during the review period in a way that makes `period_allocation` numbers incomparable to prior periods. Surface this and ask whether to proceed (with caveats) or defer.

## Failure modes

### Named failure mode (the one this skill exists to catch)

- **Portfolio drift.** The portfolio that exists now is the residue of accumulated past decisions, not the portfolio anyone would intentionally author today. Each bet was individually justified at some point; the collective allocation no longer is. The surface signal — stable composition, defensible per-bet stories, total spend consistent with last period, no bet killed in 6+ months — hides incoherent marginal allocation: bets that should be wound down continue because killing them is socially expensive; bets that should be amplified aren't because reallocation is operationally expensive; candidates sit parked indefinitely because deciding either way costs political capital. The skill's second-axis check is the zero-based reallocation: if the portfolio were re-authored from scratch today, what would it look like? Bets that don't survive a zero-based authoring are portfolio drift candidates. See [`GLOSSARY.md#portfolio-drift`](../../GLOSSARY.md#portfolio-drift).

### Other failure modes

- **Status-quo anchoring.** Generating the zero-based hypothetical *after* inspecting the actual allocation. The actual portfolio anchors the hypothetical; drift is invisible. The process step ordering exists to prevent this; do not soften it.
- **Halo allocation.** A successful flagship bet's halo justifies continued investment in adjacent bets that haven't earned it independently. Flag explicitly per [`allocation-patterns.yaml`](allocation-patterns.yaml).
- **Sunk-cost drift.** Bets continue because the team has accumulated investment, not because the forward-looking case is strong. The `latest_tenets_review` evidence is the forcing function; sunk cost is not a valid `triggering_evidence`.
- **Diversification theater.** Spreading capacity across many small bets and calling it "portfolio diversification" when no individual bet has the capacity to validate or fail cleanly. A bet that cannot fail-fast cannot be portfolio-managed; it is overhead.
- **Quiet candidate parking.** Candidates accumulate in the `continue_to_park` bucket every period without ever being funded or rejected. The "candidates evaluated" gate forces a decision; do not soften it.
- **Kill-list theater.** Producing a "kill list" that doesn't include anything the team has political capital invested in. If every wind_down recommendation is on a low-profile bet, the review is performative; flag it.
- **Founder flagship protection.** The bet originated by the most senior person on the team gets a different evidentiary standard than other bets. Surface this against `allocation-patterns.yaml` and run the zero-based check ignoring origin.
- **Narrative laundering.** A `portfolio_narrative` that emphasizes totals and obscures kills. The narrative must surface the kills and the reallocations, not bury them.

## Reviewer pass

After emitting, run a second pass that checks:

- `zero_based_reallocation` was generated before `bet_recommendations` (the schema's ordering is enforced; the process must match).
- Every `bet_recommendations[]` has `triggering_evidence` that cites a specific artifact (tenets-review output, AGG output, WBR variance, or named external context) — not prose.
- Every `candidate_decisions[].fund` has a named `opportunity_cost_against`.
- `review_integrity.changes_made == false` only if `zero_based_passed == true` AND `status_quo_justification` names each bet explicitly.
- `kill_candidates_considered` is non-empty even when no kill is recommended — the review must consider kills, not assume their absence.
- `drift_detected` is non-empty if any `drift_from_actual[]` entry has a non-zero `delta` — drift was named, not glossed.

## Follow-up mechanism

- Each `bet_recommendations[].wind_down` triggers a wind-down PRFAQ (uses `working-backwards-prfaq` with `target_artifact: kill_decision` — the existing PRFAQ skill handles termination decisions).
- Each `bet_recommendations[].amplify` or `pivot` triggers a fresh `mechanism-designer` run to operationalize the change.
- Each `candidate_decisions[].fund` triggers a `working-backwards-prfaq` for the candidate if its existing PRFAQ is older than two review periods.
- Any reallocation that crosses an irreversibility threshold (terminating a contract, releasing staff, public announcement) MUST pass through `dissent-before-commit` before execution.
- The full `portfolio-review` output is archived. The next portfolio-review consumes it as `prior_portfolio_review`; drift patterns that persist across reviews are escalating evidence.

## Handoffs

**Consumes from**

- `tenets-review`: `current_recommendation` per bet → `latest_tenets_review`; chronic-pattern findings inform `bet_recommendations` rationale
- `ambitious-goal-grading`: `attainment + calibration` per bet → `latest_goal_grading`; chronic sandbagging is a signal that the bet's `expected_return` may have been overstated at authoring
- `weekly-business-review`: aggregated period variance per bet → `cumulative_wbr_variance`; materialized risks → context
- `working-backwards-prfaq`: original `success_metrics`, `risks`, `mvp_boundary` → context for evaluating drift against the bet's authoring contract
- Prior `portfolio-review`: full output → `prior_portfolio_review` (persistent drift is escalating)

**Feeds into**

- `working-backwards-prfaq`: `bet_recommendations[].wind_down` → kill-decision PRFAQ; `candidate_decisions[].fund` → re-author the candidate's PRFAQ if stale
- `mechanism-designer`: `bet_recommendations[].amplify` and `pivot` → new mechanism inputs
- `dissent-before-commit`: any reallocation crossing an irreversibility threshold → `proposed_action`; `drift_detected` evidence → `state_changes_since_authoring`
- `tenets-review`: a `wind_down` recommendation that is being resisted → trigger `tenets-review` with `review_trigger: portfolio_review_kill_disputed` for an independent thesis check

Enums used: `portfolio_bet_recommendation`, `candidate_decision`, `allocation_change_severity`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

## Why this skill is not a `required_review` on `tenets-review`

`tenets-review` operates per-bet; `portfolio-review` operates across bets. They are different units of analysis. Requiring `portfolio-review` after every `tenets-review` would force cross-bet review at single-bet cadence, which is wrong — and would create a circularity (portfolio-review consumes from tenets-review). The skills compose at period boundaries, not as a synchronous review chain. `portfolio-review` is invoked when the period closes; `tenets-review` is invoked event-driven and on shorter cadence.

## Influence attribution

This skill draws on traditions outside Amazon. Google's OKR/portfolio-review cycle surfaces the cross-bet allocation question explicitly. Venture-capital portfolio management contributes the "marginal dollar" framing and the discipline of opportunity-cost comparison against an external alternatives set. The zero-based reallocation second-axis check is borrowed from zero-based budgeting (originating in 1970s public-sector finance, popularized in tech contexts). The suite's `## Influences` section in [`README.md`](../../README.md#influences) attributes these explicitly.

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
