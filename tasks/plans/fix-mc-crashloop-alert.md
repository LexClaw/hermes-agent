# Fix Plan — Bug 2: Mission Control crash-loop has no alert path

**Card:** (filled after creation)
**Owner:** Reid implements. Grant eng-reviews this plan first.
**Type:** Observability gap fix (additive, low-risk). Carved out of the scheduler fleet audit as fix-now.
**Severity:** P1 — a ~3-hour silent prod outage happened TODAY (2026-06-03, 09:15-12:23 ET) with zero alert.

## Problem (verified 2026-06-03)
The `mission-control` pm2 process crash-looped for ~3 hours today: incomplete `.next` build artifacts triggered relaunch storms, 177 circuit-breaker fires logged. The circuit breaker WORKED (clean exit, eventual recovery at 12:23, now stable). pm2 `restart_time` is 2105 cumulative.

**The gap:** nothing alerted. `mc-healthcheck.sh` (the existing watcher, every 5min) only probes the `/api/internal/healthz` endpoint with `ALERT_THRESHOLD=2` + 1800s cooldown. During a relaunch storm the endpoint FLAPS — it briefly responds between restarts — so the consecutive-failure threshold never trips. A process thrashing through 177 restarts can look "healthy enough" to an endpoint poller while being completely down for users.

**Root cause:** we monitor the endpoint (a symptom that flaps), not the pm2 restart-count (the actual crash-loop signal).

## GRANT PLAN-REVIEW VERDICT (2026-06-03): CHANGES_REQUIRED — 4 required changes folded in below
Direction approved (extend mc-healthcheck.sh, restart_time delta is the right signal). Four required implementation constraints, all confirmed against the live script:

**RC-1 — First-run baselining (CRITICAL, prevents false alert on deploy).** Current cumulative restart_time is 2105. If the script defaults a missing `last_restart_time` to 0, the very first run computes delta=2105 and fires a false crash-loop alert immediately. REQUIRED: on first run, missing key, unreadable state, OR a current value LOWER than previous (pm2 counter reset), SEED `last_restart_time` to the current value and do NOT alert. Only alert on a genuine forward climb of >= N within one interval.

**RC-2 — Independent cooldown state.** The existing script has ONE `last_alert_ts` shared with the endpoint path. Reusing it lets an endpoint alert suppress a crash-loop alert and vice-versa — which would re-create the exact blind spot (endpoint flaps green while restarts climb). REQUIRED: add a SEPARATE `last_restart_alert_ts` (keep the existing endpoint `last_alert_ts`/`consecutive_failures` fields untouched). The two alert paths must not be able to suppress each other.

**RC-3 — Restart check runs BEFORE the HTTP-200 early exit.** The existing script exits immediately on HTTP 200 (lines 65-70). During a relaunch storm the endpoint returns a transient 200 between restarts — so if the restart check is only on the failure path, the incident pattern stays invisible. REQUIRED: read + evaluate pm2 restart_time on EVERY invocation, including healthy-endpoint runs, before any success exit.

**RC-4 — pm2-unavailable is a non-silent failure.** If pm2 is missing from PATH, `pm2 jlist` errors, mission-control is absent from the list, or restart_time is null/non-numeric, the new signal must NOT silently degrade (the endpoint can still pass during a storm). REQUIRED: handle these explicitly — log a SANITIZED error and preserve prior state; do not let `set -e` abort before the endpoint probe + delivery. Optionally alert (same cooldown) if restart-monitoring itself is down.

## Fix (additive — do NOT touch the working circuit breaker)
Add a pm2-restart-rate alert. Two viable shapes, Reid picks the simpler that fits:
1. **Extend `mc-healthcheck.sh`:** in addition to the endpoint probe, read `pm2 jlist`, extract `mission-control`'s `restart_time`, persist last-seen value to a state file, and if `restart_time` climbs by >= N (e.g. 5) within one check interval, alert to LexTech (telegram:-1003914984528:256, the ops thread). This is the leanest — one watcher, two signals.
2. **Standalone tiny watcher cron:** a `no_agent` jobs.json cron (every 5-10min) that does only the restart-delta check. Use only if folding into mc-healthcheck.sh muddies it.

Preferred: option 1 (extend the existing healthcheck — fewer surfaces, consistent with the addition-by-subtraction goal of NOT adding new crons).

Alert payload must include: process name, restart_time delta, current status, and the likely cause hint ("check .next build artifacts / relaunch storm").

## Acceptance
1. A simulated or real restart-count climb of >= N in one interval produces exactly one alert to LexTech (respecting a cooldown so a storm doesn't spam).
2. The endpoint probe behavior is unchanged (no regression to the working check).
3. The circuit breaker is untouched.
4. State file persists last-seen restart_time across runs so deltas are computed correctly.
5. Documented: what N and cooldown are, and why.

## Reversibility / safety
- Purely additive to an existing script or one new tiny cron. No change to MC itself, no change to the circuit breaker.
- If the alert is too noisy, tune N/cooldown or revert the script edit (git). Fully reversible.

## Note (out of scope, flag only)
Arm C flagged a P1 secret-leak: `pm2 jlist` exposes Twilio/X/Google tokens in plaintext env. Do NOT print full `pm2 jlist` output to any log or alert. When reading restart_time, extract ONLY that field — never echo the env block. Flag the broader secret-in-pm2-env issue to TJ as a separate item; do not fix it in this card.
