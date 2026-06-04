# MASTER PLAN — Addition by Subtraction: Hit Network Agent Stack to Garry-Tan Elegance

**Card:** kn74s7r0k7rh78n8wsy75enxd187yfwm
**Synthesized by:** Lex (orchestrator), 2026-06-03, from a 3-wave multi-model fleet:
- Wave 0: exhaustive surface discovery (6 schedulers confirmed, nothing missed)
- Wave 1: 3 parallel surface audits (Reid/GPT-5.5 on jobs.json, Grant/Opus on shadow layer, Grant/Opus on Convex+pillars) + 3 prior root-cause arms (Lex+Grant/Opus, Grant/GPT-5.5)
- Wave 2: structured debate, elegance-maximalist (Opus 4.8) vs operational-safety (GPT-5.5)
**Status:** PLAN ONLY. Nothing in Phases 1+ executes without TJ approval. Two P1 bugs already fixed+shipped (carved out, TJ-approved).

---

## 1. THE COMPLETE SURFACE MAP (the "are we missing anything" answer)

**SCOPE NOTE (corrected after final review GAP 1):** This plan governs the SCHEDULER surfaces AND the SKILL corpus — both halves of the Foxconn factory. The final adversarial review caught that v1 silently narrowed to schedulers only, dropping the skill layer that 3 of 5 root-cause arms flagged as half the disease. Skills are now Phase 5b (not deferred, not asserted-sound).

Six SCHEDULER surfaces, ~151 automated entities, PLUS the skill corpus (122 hit-network prunable skills of 345 total). Verified, not assumed:

| # | Surface | Count | Owns |
|---|---------|-------|------|
| 1 | Hermes `jobs.json` | 86 jobs | the bulk of agent automation |
| 2 | user `crontab` | 22 lines | legacy scripts (the shadow layer) |
| 3 | `~/Library/LaunchAgents` | 35 plists | daemons + some duplicated scripts |
| 4 | Convex crons (MC) | 6 | DB-invariant maintenance |
| 5 | `gbrain autopilot` daemon | 1 (ALL_PHASES) | GBrain self-maintenance (native) |
| 6 | pm2 | 2 | mission-control web + tandem |
| 7 | **SKILL corpus** | **122 hit-network (345 total)** | **the other half of the ratchet — addition via skillify, no subtraction** |

Confirmed absent: system LaunchDaemons, `at`, `/etc/periodic` customizations, rogue node/bun watchers.

## 2. ROOT CAUSE (unanimous across all 5 model-arms, both families)

**A one-way ratchet.** Every improvement engine ADDS (skillify, Dreamer, SIE-proposer, MC Feature Suggester, wiring-gate) and runs on cron. NOTHING owns subtraction. The retirement organ was *specced 2026-05-30 and never shipped* to Grant's charter (proven by mtime diff). The 151 entities, the 6 surfaces, the double-fires — all symptoms of that single structural gap. **Fix the ratchet and the count finds its own floor; cut the count without fixing the ratchet and it re-accumulates.**

## 3. THE RECONCILED PRINCIPLE (where the debate landed)

The two debaters agreed on the diagnosis and ~80% of the plan. The one real tension — "fix aggressively" vs "instrument first" — resolves with a single classification rule both sides accept:

> **CONFIRMED BUG vs REDUNDANCY HYPOTHESIS.**
> - A **confirmed bug** (double-fire racing the same store, ghost script firing against a missing file, broken job erroring every run) is NOT a redundancy hypothesis. You cannot soak a ghost. Fix it now, with verification (not a 7-day soak).
> - A **redundancy hypothesis** ("these 4 watchers MIGHT catch distinct failures") MUST be soak-gated: prove coverage parity in shadow mode for 7 days before retiring anything.

This is the synthesis. It gives elegance its aggressive bug-fixes AND gives safety its prove-before-prune on everything that touches a producer or an unproven failure-class.

## 4. NON-NEGOTIABLE GUARDRAILS (safety arm, fully adopted)

Every consolidation in Phases 2+ MUST have these BEFORE it ships:
1. **Instrument before retire.** Snapshot jobs.json + crontab + launchd to a git-tracked location FIRST. Add `owner` / `subsystem` / `output_contract` / `alert_contract` / `retirement_candidate` metadata to every job before any cut.
2. **Positive-assertion liveness** on every consolidated supervisor — it emits a heartbeat row even when healthy, so SILENCE is the alarm (not just an error).
3. **External dead-man** on the watcher-of-watchers. The one cron-scheduler supervisor must be monitored by something it does NOT monitor itself (launchd dead-man or MC healthcheck). No N-to-1 watcher collapse ships until this exists.
4. **7-day shadow parity** before retiring any soak-gated job: the new supervisor must surface every failure the old N caught, at equal-or-higher rate.
5. **Move, don't delete.** Comment crontab (never rm), `launchctl unload` + move plist to `_deprecated/`, soft-delete skills with recovery window. Every change reversible in <1 min.
6. **No count target as success metric.** The number going down is a CONSEQUENCE of fixing the ratchet, never the goal. Success = bidirectional loop + zero confirmed bugs + no new SPOF.

## 5. PHASED PLAN

### Phase 0 — Ship the missing organ (DO FIRST, leanest possible, fixes the root cause)
Land the subtraction-scan bullet that was specced 2026-05-30 and never shipped, into Grant's AGENT.md Section 13 (Weekly Drift Audit), framed as the dual of the wiring-gate: "for each cron/skill/script across ALL 6 surfaces: is this still firing, still read, still distinct from a sibling? Flag-only output; propose retirements through the soak gate; never auto-delete." Use existing issue taxonomy. NO new cron. Wire it to the existing Sunday drift run. Effort ~1h, risk near-zero (additive, flag-only).
**This is the highest-conviction recommendation of the entire fleet.**

### Phase 1 — Fix CONFIRMED BUGS now (no soak; verification only)
- [DONE] task_index_sync.py retired (was failing 96x/day on npx). Shipped, verified, in_review. (GAP 9: verify the surviving jobs.json `sync_task_index_from_convex` .sh actually wraps the .mjs canonical writer and covers the retired job's intent — one verification line.)
- [DONE] MC crash-loop alerting added (3h silent outage today). Shipped, verified, in_review.
- **GAP 2 — CONFIRM/RESTORE THE 72% SKILL-INJECTION REGRESSION (highest priority, may be LIVE).** The 2026-05-30 un-gated matcher change (relevance_floor 0.4→0.6, top_n 25→7) cut skill injection ~72% per dispatch. FIRST ACTION: confirm whether it was reverted. If NOT reverted, the system is shipping degraded dispatches RIGHT NOW — restore the defaults immediately (this is a confirmed bug by our own rule, not context). THEN add a selector-regression + prompt-compile-diff test harness — this is the PREREQUISITE that gates all skill work in Phase 5b.
- ale_recommendations.py — ghost script (file absent, 100% file-not-found) firing 2x/day on crontab+launchd. Retire both. (True confirmed bug: you cannot soak a ghost.)
- ale_pattern_detect.py — 6th double-schedule (cron + launchd, same log). Dedup.
- **Memory DAG reconciliation (generate → index → distill → health), SEQUENCED not raced in the 23:00-23:45 window. This is INVESTIGATE-then-fix (diff the scripts first), covering ALL THREE indexers:**
  - memory-auto-indexer.py — fires 1 second apart from two schedulers against the same store (live race). Dedup to one.
  - memory_distill.py — two different script COPIES at different paths, double-scheduled. Reconcile to one canonical.
  - **nightly-auto-indexer.py (GAP 4) — the THIRD indexer (launchd 23:00, last-exit 2), runs 15 min before memory-auto-indexer, likely a superseded predecessor. Diff against memory-auto-indexer; do not let a 3rd writer to the same store survive unlisted.**
  - **wiki-indexer.py dead dependency (GAP 7) — memory-auto-indexer logs `[WikiIndex] SKIP: wiki-indexer.py not found` every night (silent partial-failure from the 2026-05-15 wiki retirement). Either restore it or remove the dead call.**
- **tailscale-keepalive (GAP 3 — SPLIT per the bug-vs-hypothesis rule):** the exit-127 (binary not found) IS a confirmed-broken signal — surface it now. But "retire because redundant with the macsys Tailscale app" is a HYPOTHESIS (arm-b said INVESTIGATE-then-retire). So: flag the exit-127 now, but the retire waits on verifying the macsys app actually covers it. Do NOT no-soak-retire it.

### Phase 2 — Instrument (the safety prerequisite for all consolidation)
Snapshot all surfaces to git; add owner/output/alert/retirement metadata to every job; build the positive-assertion-liveness + external-dead-man scaffold. NO retirements yet. This is the "add one small thing (a dead-man) to safely subtract four" move both arms endorsed.
- **GAP 6 — read the launchd exit codes.** Six nightly `ai.hitnetwork.*` jobs (lock-check, memory-health-check, nightly-auto-indexer, promotion-check, reconcile-completed, wal-checkpoint) exit non-zero (1 or 2) every run with NO alerting watching exit codes. This is a free, untapped failure signal. Phase 2 instrumentation MUST include "reconcile each non-zero launchd exit: intentional vs silent failure" as an explicit checklist item — don't snapshot a fleet whose failure signals were never read.

### Phase 3 — Soak-gated consolidations (redundancy hypotheses, one cluster at a time)
Each behind 7-day shadow parity + the Phase 2 guardrails:
- GBrain guard cluster 8 -> 1 supervisor that consumes native `gbrain doctor --json`/`gbrain health` + the few checks doctor lacks (export freshness, backup-restore, central-node). **Biggest elegance win, but rests on the one unverified assumption (arm-c Risk 7): does the autopilot daemon's internal cycle + doctor actually cover the bespoke cluster deeply enough? VERIFY the autopilot cycle interval first.**
- Cron-scheduler safety 4 -> 1 supervisor (ships ONLY after external dead-man exists).
- MC guard cluster -> 1 supervisor; resolve the Convex `approval_pending_mark_stale` vs Hermes duplicate (keep Convex, retire Hermes cron). **GAP 5 — PREREQUISITE: add a Convex failure-signal/alert path BEFORE retiring the Hermes cron.** Convex crons currently have no sub-5-min failure signal (only a weak weekly liveness check). Retiring the redundant Hermes owner without instrumenting the surviving Convex owner trades duplication for a blind spot — strictly worse observability. Instrument the survivor first, then retire the duplicate.
- Routing-intel 5+ -> 1 staged loop.
- Meet EA 4 one-minute crons -> 1 queue poller / event-driven.
- Daily-curated-writer 4 -> 1 time-gated job.

### Phase 4 — Drain the shadow layer
Migrate surviving unique crontab batch jobs into jobs.json for unified governance. launchd keeps daemons ONLY. End-state: crontab near-zero, launchd ~18 daemons.

### Phase 5 — 3-pillar architecture (the deepest work, do last)
- Pillars 1 (Brain) + 2 (Skills) are Garry's own designs and sound — the work is removing scaffolding bolted ON TOP, not touching the pillars.
- **Pillar 3 (SIE) is where the SCHEDULER sprawl concentrates.** Canonical membership (GAP 8): arm-a's enumerated **17 SIE jobs** are the SIE set; routing-intel's **5** are a named sub-cluster (some arms folded them together → the "~20" figure). Phase 3 consolidates SIE and routing-intel as separate clusters; Phase 5 re-merges into ONE staged self-improvement loop with one arbiter and a BUILT-IN subtraction guard — making SIE itself bidirectional. This is where SIE stops being sprawl and becomes the engine that retires sprawl.

### Phase 5b — SKILL corpus consolidation (the 7th surface; GATED on Phase 1 regression harness)
The skill layer is HALF the Foxconn factory and was nearly dropped (final-review GAP 1). 122 hit-network prunable skills, 35,544 lines, with a retrieval/bias tax (a narrow skill loading in the wrong task becomes behavior, not just docs). Gated on the Phase 1 selector-regression harness (cannot prune skills safely without it — the 72% regression is the proof).
- Verify-then-scrub already-consolidated dirs (gbrain-link-recovery absorbed ~25; confirm gone, not lingering).
- Archive confirmed dead weight: `task-skills-v15-backup/` (loose .md files, not even SKILL.md format) through move-and-soak.
- Integrate with the existing Curator (`agent/curator.py`, skill-only, archives don't delete) rather than duplicating it — extend its scope or feed it the cross-surface subtraction-scan output.
- Line-count hotspots (mission-control-board-prod-vs-dev 880, grant-mc-verdict 772, prompt-compiler-operations 754) are NOT auto-prune targets — large ≠ bad; assess by load-frequency + retrieval value, not size.
- Every prune: propose → TJ-approve → soft-delete with recovery window. Skill changes MUST pass the regression harness.

### Phase 6 (optional) — Promote subtraction scan from flag-only to standing proposer
ONLY after the Phase 0 bullet has fired on real data and produced >=1 good catch. Do NOT build the retirement ENGINE before the retirement BULLET earns it (building it preemptively would itself be the Foxconn anti-pattern).

## 6. END-STATE (the number is downstream, cited only to make it concrete)
~4 schedulers of record (from 6); jobs.json ~40 (from 86); crontab ~0; launchd ~18 daemons; Convex 5; autopilot absorbs its 8 external supervisors. The real deliverable: **the improvement loop becomes bidirectional.**

## 7. OPEN ITEMS FOR TJ (decisions / flags)
1. **Approve the phased plan** (or adjust sequencing/aggression).
2. **Security flag (separate from this plan):** `pm2 jlist` exposes Twilio/X/Google tokens in plaintext env (arm-c P1). Worth its own remediation.
3. **The one load-bearing assumption** the biggest elegance win rests on: whether `gbrain` native autopilot+doctor covers the bespoke GBrain health cluster. Phase 3 verifies it before retiring those 8 crons; if it doesn't cover them, those crons STAY.

## 8. COVERAGE CERTAINTY STATEMENT
All 6 SCHEDULER surfaces discovered and independently audited; no 7th scheduler exists (system LaunchDaemons / at / periodic confirmed absent). The SKILL corpus (the non-scheduler surface 3 root-cause arms flagged) is now explicitly in scope as Phase 5b after the final adversarial review caught v1 silently dropping it. Root cause confirmed by 5 model-arms across 2 families. Strategy stress-tested by an adversarial 2-perspective debate, then the synthesis itself was adversarially reviewed (caught 6 blocking gaps, all now folded in). The known unknowns are named explicitly: (a) item 7.3 — whether gbrain native autopilot+doctor covers the bespoke GBrain health cluster (Phase 3 verifies before retiring); (b) the live status of the 72% skill-injection regression (Phase 1 first action). I am confident no entire surface is missing and the plan accounts for the scheduler fleet, the skill corpus, and all 3 pillars. Remaining risk lives in the two named known-unknowns, not in unscoped surfaces.
