# Correction of Errors — INC-2026-09-17-01

> Worked example. Hypothetical incident on the ChangeLens product carried over from `01-working-backwards-prfaq/examples/example-prfaq.md`. Demonstrates blameless tone, multi-factor Five Whys, and detection/prevention separation.

---

## Incident Summary

On 2026-09-17 between 18:00 and 18:40 UTC, ChangeLens served stale or empty weekly digests to 41 of 87 active customer teams (47%) during the Tuesday-evening digest pre-generation window. Customer impact: 41 EMs opened a draft that was empty or referenced last week's PRs. Three customers contacted support.

- **Incident ID:** INC-2026-09-17-01
- **Date:** 2026-09-17
- **Duration:** 40 minutes (18:00–18:40 UTC mitigation; full recovery 19:12 UTC)
- **Severity:** SEV-2

## Customer Impact

- **Customers affected:** 41 of 87 active teams (47%) `[fact — server logs]`
- **Requests / digests impacted:** 41 digest pre-generations served stale or empty data
- **Money:** No revenue impact (no SLA tier yet)
- **Trust signals:** 3 support tickets, 1 Slack DM to PM, 0 churn intent. One ticket: "Is this thing broken? My digest has nothing in it." `[fact — support ticket #883]`

## Timeline

| Timestamp (UTC) | Event | Source |
|------------------|-------|--------|
| 17:50 | GitHub API began returning 5xx on `/repos/.../pulls` endpoint | github status page |
| 18:00 | ChangeLens digest pre-generation cron started | scheduler logs |
| 18:00 | First failed `GET /pulls` for cohort batch 1 | app logs |
| 18:01 | Retry logic exhausted (3 retries, 2s backoff); empty result cached | app logs |
| 18:06 | First customer support ticket filed | Zendesk |
| 18:14 | On-call paged via Datadog alert (digest_gen_error_rate > 5%) | Datadog |
| 18:19 | On-call confirmed GitHub-side issue | github status |
| 18:32 | Manual cache flush executed; pre-generation re-triggered | runbook |
| 18:40 | Pre-generation completed for all 87 teams | app logs |
| 19:12 | Final affected customer confirmed fresh digest | support follow-up |

## Facts

- `[fact]` GitHub's `/pulls` endpoint returned elevated 5xx between 17:50 and 18:40 UTC. Confirmed at status.github.com.
- `[fact]` ChangeLens retry config: 3 retries, exponential 2s/4s/8s backoff. Source: `config/github_client.yaml`.
- `[fact]` On exhausted retry, the client returns an empty list rather than raising. Source: `github_client.py:142`.
- `[fact]` Empty results were cached with the same TTL as successful results (24h).
- `[inference]` Customers with smaller PR volumes were more likely to see empty digests during the window. Not verified.
- `[open question]` Why was the on-call alert delayed 14 minutes? Datadog metric latency or alert threshold?

## Five Whys

### Contributing factor A: empty results were cached as successes

1. Why did 41 teams get empty digests? Because the GitHub client returned empty lists during the outage and those lists were cached.
2. Why did the GitHub client return empty lists? Because the retry-exhaustion path returns `[]` instead of raising.
3. Why does retry exhaustion return `[]`? Because the client was designed to "fail soft" so a single bad repo would not break the whole digest.
4. Why does fail-soft cache empty results with full TTL? Because the cache layer treats successful and empty responses identically — there is no concept of "empty due to upstream failure".
5. Why is there no such concept? Because the cache schema does not record provenance (origin: upstream success, upstream empty, upstream failed). The system cannot distinguish a real "no PRs this week" from a "GitHub said nothing".

### Contributing factor B: alert latency

1. Why did the on-call get paged 14 minutes after the first failed call? Because the Datadog alert fires on a 5-minute rolling error rate above 5%.
2. Why a 5-minute window? Because shorter windows produced false positives during deploys.
3. Why during deploys? Because the deploy briefly drains in-flight digest jobs without filtering them out of the error metric.
4. Why no filter? Because the metric was set up before the deploy flow was finalized, and no one revisited it.
5. Why was it not revisited? Because there is no recurring inspection of alert thresholds against current deploy behavior.

## Root Cause

The cache schema does not record provenance, so empty upstream responses are cached as if they were genuine "no data". A transient GitHub outage during the daily pre-generation window produces up to 24 hours of stale digests for any team whose batch ran during the outage.

The contributing alert-latency gap is a separate system condition: deploy-induced false positives drove the alert threshold up, but the threshold was never revisited after the deploy flow stabilized.

## Detection Gap

- The on-call alert fires at >5% error rate over 5 minutes. Customers experienced impact for 14 minutes before paging.
- No synthetic check confirms that a freshly generated digest is non-empty for a known-active canary team.

## Prevention Gap

- The GitHub client conflates "empty due to no PRs" with "empty due to upstream failure".
- The cache layer has no concept of response provenance.
- There is no recurring inspection of alert thresholds against current deploy behavior.

## Action Items

| # | Action | Type | Owner | Due |
|---|--------|------|-------|-----|
| 1 | Add response-provenance tag to cache entries (`upstream_ok`, `upstream_empty`, `upstream_failed`); refuse to cache `upstream_failed` | prevention | Eng lead | 2026-09-30 |
| 2 | Make `github_client` raise (not return `[]`) on retry exhaustion; let the caller decide | prevention | Eng | 2026-09-25 |
| 3 | Add synthetic check: confirm a fresh digest for at least one canary team is non-empty within 5 minutes of pre-generation | detection | SRE | 2026-10-07 |
| 4 | Establish a quarterly mechanism to review alert thresholds against the current deploy flow | process | SRE | First review 2026-10-15 |

## Owners and Due Dates (consolidated)

| Owner | Action items |
|-------|--------------|
| Eng lead | 1 |
| Eng | 2 |
| SRE | 3, 4 |

## Follow-Up Mechanism

- **Follow-up date:** 2026-10-15
- **Owner:** Eng lead
- **Confirms:** Actions 1–3 shipped to production; alert-threshold review (action 4) held with notes; no re-occurrence of the empty-digest pattern in the interim.

## Prior incidents of this class

| Incident ID | Date | Same root cause? |
|-------------|------|-------------------|
| INC-2026-07-02-03 | 2026-07-02 | Adjacent — empty Linear digest from a different upstream outage. Same provenance gap; was attributed at the time to "Linear flakiness" without a CoE. This CoE supersedes that classification. |
