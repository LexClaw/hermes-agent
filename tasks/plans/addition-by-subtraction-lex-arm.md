# Addition-by-Subtraction Audit — Lex (Opus 4.8) Independent Arm

**Card:** kn74s7r0k7rh78n8wsy75enxd187yfwm
**Method:** gstack-investigate (root-cause, not symptom). Symptom = "system feels bloated, hard to maintain, struggling." Root-cause question = where is the Foxconn factory.
**Baseline:** 86 crons, 345 SKILL.md files (127 top-level dirs), brain_score 91/100.

> NOTE: this is the INDEPENDENT Lex arm. Grant (GPT 5.5) runs a blind parallel audit. Do not reconcile here — reconciliation happens in the cross-modal debate.

## Iron Law finding: the root cause is NOT "too many skills/crons"

The naive read is "delete stuff." That is symptom-fixing and it is dangerous (blind deletion breaks the loop). The ROOT cause, in Garry's framing, is **we wrote code/config to babysit a model that no longer needs babysitting, and we never built the mechanism to retire that scaffolding.** Three structural findings:

### Finding 1 — The cron layer is 33% self-surveillance (Garry's "33 alarms" almost exactly)

28 of 86 crons (33%) are guard/watchdog/audit/monitor-shaped. The damning part is the OVERLAP — we have multiple independent crons watching the same subsystem:

- **Cron system watching itself (4 crons):** Cron Health Monitor (2h), Cron-Heartbeat Watchdog (4h), Stale Cron Path Watcher (23:55), Jobs.json Shrink Alarm (30min). Four alarms guarding the alarm system.
- **GBrain watchers (6+ crons):** Daily Health Check (9am), Autopilot Health Audit (11:05), Brain-Growth Audit (11am), Central-Node Audit (weekly), Export Watchdog (6am), Weekly Maintenance (Mon). Plus the embed safety-net and link-rebuild. GBrain has its OWN `gbrain doctor` + autopilot; we bolted a second supervision layer on top of a system that already supervises itself.
- **MC watchers (5 crons):** mc-healthcheck (5min), MC Drift Watchdog (hourly), MC Stuck in_progress Audit, MC Approval Pending Poller, MC Authed Cron Liveness Check.

This is the literal Foxconn pattern: redundant guardrails bolted onto workers (GBrain autopilot, the scheduler, MC) that already do the job. **The fix is not "delete watchdogs" — it is "collapse N overlapping watchers into 1 supervisor per subsystem, and trust the subsystem's own health surface where it exists."**

### Finding 2 — Skill count is inflated by vendored upstream + already-retired-but-not-deleted

345 SKILL.md is misleading. Decompose:
- **gstack-* : 48** — these are GARRY'S OWN upstream skills (vendored). Pruning them is wrong; they're maintained upstream. They should arguably not even count toward "our" surface.
- **gbrain-* : 22** — GBrain's shipped skills, similar story (his design).
- The real prunable surface is the **Hit Network custom skills** under ~/.hermes/skills/hit-network/. Several clusters were ALREADY consolidated (e.g. gbrain-link-recovery absorbed "25 retired source skills" per its own header) — need to verify the 25 retired dirs are actually gone vs. lingering as dead weight.
- **Root cause here:** no retirement mechanism. Skills get created (skillify is good at addition) but nothing subtracts. Same disease as crons.

### Finding 3 — THE missing organ: a retirement/pruning loop (this is what never got built into Grant)

TJ's verification question — "was addition-by-subtraction built into Grant's design?" — answer: NO (confirmed empty in session history + brain). This is the actual hole. We have:
- Addition engines: skillify, Overnight Dreamer, Feature Suggester, SIE proposer (all CREATE).
- Zero subtraction engine. Nothing periodically asks "what cron fired 500x and produced nothing? what skill hasn't been loaded in 60 days? what guardrail never caught anything?"

Garry's stack stays elegant because `skillify` bundles tests+evals+resolver so a skill can CHANGE without breaking — and dead ones get pruned. We have the addition half, never built the subtraction half.

## Lex proposed plan (3 moves, elegant > aggressive)

**Move 1 — Consolidate overlapping watchers (not delete).** One supervisor cron per subsystem:
- 4 cron-watchers -> 1 "scheduler supervisor" (liveness + shrink + stale-path + heartbeat in one no_agent script).
- 6 GBrain-watchers -> 1 thin watcher that reads `gbrain doctor --json` (GBrain already supervises itself; we consume its surface instead of re-deriving it). Net: trust the worker's own health endpoint.
- 5 MC-watchers -> 1 MC supervisor.
- Estimated: 28 guard crons -> ~8. Addition by subtraction via consolidation, zero capability lost.

**Move 2 — Build the subtraction engine (the thing that never got built).** A weekly "prune proposer" (the missing Grant organ): reads ALE skill-load telemetry + cron fire/output ratios, proposes retirement candidates (skill not loaded in N days, cron that produced zero deliverables in N fires, guardrail that never tripped). Proposes to a Proposals column; TJ approves. This is the self-improving subtraction loop, symmetric to skillify's addition.

**Move 3 — Verify-then-scrub the already-retired skills.** Confirm the ~25 gbrain-link-* and other consolidated-but-maybe-lingering dirs are gone; remove dead weight with the supersede-verify-scrub discipline (never scrub on faith).

**Guardrail-to-capability principle (the durable rule):** before adding ANY new watchdog/guardrail cron, the test is Garry's — "is this catching a failure the worker actually makes, or is it an alarm for a worker who shows up on time?" If the subsystem has its own health surface, consume it; don't re-derive it.

## Honest caveats / risks
- Consolidating watchers has a real risk: a single supervisor failing is a single point of failure where 4 independent ones had redundancy. Mitigation: the one supervisor must itself be dead-simple and have an external liveness ping (the one alarm that earns its keep).
- "Addition by subtraction" can overcorrect into "delete things that were quietly load-bearing." Every prune goes through propose -> TJ-approve -> soft-delete-with-recovery-window. Never hard delete.
- gstack/gbrain vendored skills are OUT of scope for pruning (upstream-owned).
