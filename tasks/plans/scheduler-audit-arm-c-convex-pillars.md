# Scheduler Fleet Audit, Arm C: Convex Crons + GBrain Autopilot + PM2 + 3-Pillar Integration

**Auditor:** Grant (Sr. Systems Engineer, Engineering Critic)
**Date:** 2026-06-03
**Mode:** Analysis only. Nothing changed. MC git working tree confirmed untouched by this audit.
**Methodology:** gstack-investigate. Verify reality on disk, not docs. Reference GStack/GBrain elegance standards.
**Scope:** Arm C of a 6-surface fleet audit. I own Convex crons, the GBrain autopilot daemon, PM2, and the cross-cutting 3-pillar analysis. Other arms own `jobs.json` enumeration and the crontab/launchd shadow layer. Conclusions here are independent.

**FINAL OUTCOME (one line):** A named, evidence-backed map of where Convex crons race Hermes-side MC crons, where 19 external GBrain crons re-derive work the autopilot daemon already does, the verdict on mission-control's 2105 PM2 restarts, and where the Brain/Skills/SIE pillar application itself manufactured sprawl.

---

## VERDICT (open with the finding)

**APPROVED WITH CHANGES** as a system. It runs, it self-heals, and the dangerous overlaps are mostly guarded. But three classes of degradation are live:

1. **One genuine cross-system duplicate** that is a real race surface (`approval_pending_mark_stale`).
2. **The Foxconn pattern on Pillar 1 (Brain) is real and measurable**: a self-supervising daemon with at least 8 external crons bolted on top of it, several re-deriving native phases.
3. **PM2 mission-control suffered a real 30-minute crash loop this morning (09:15-09:44 ET).** The 2105 count is not a cosmetic counter artifact. It is the scar tissue of a recurring incident class. The circuit breaker worked. The root cause did not get fixed, it got contained.

Confidence: I stake my reputation on findings 1, 2, and the PM2 timeline. The 3-pillar sprawl read is high-confidence but is judgment, not a single cited line.

---

## SURFACE 1: CONVEX CRONS (`/Users/TJ/mission-control/convex/crons.ts`)

Six registrations, verified on disk. Each runs inside the Convex prod deployment `mellow-mule-232`, scheduled by Convex's own scheduler (NOT Hermes, NOT crontab). This is a fourth independent scheduler in the fleet.

### The six jobs

- **refresh_primary_google_calendar** , every 15 min , `internal.calendar.refreshPrimaryCalendarInternal`. Pulls the primary Google Calendar into Convex.
- **expire_stale_agent_activity** , every 15 min , `internal.activity.expireStale`. Ages out stale agent-activity rows (the live-presence indicator).
- **soak_auto_flip** , every 15 min , `internal.tasks.soakAutoFlip`. Flips cards out of the soak/in_review holding state after the soak window. Verified: `tasks.ts:513 soakAutoFlip` is an `internalMutation`.
- **grant_review_backstop** , every 15 min , `internal.reviewActions.grantReviewBackstop`. Sweeps `tasks.listByStatus("in_review")` and POSTs each to the Hermes `grant-auto-review` webhook. Verified: `reviewActions.ts:425`, pre-filters `archived !== true` (added after sentinel `kn7ft2...` re-fired Grant 4x, per AGENTS.md).
- **decision_queue_archive_stale** , daily 11:00 UTC , `internal.decisionQueue.archiveStaleResolved`. Archives resolved decision-queue rows older than 30 days.
- **approval_pending_mark_stale** , daily 12:00 UTC , `internal.approvalPending.markStale`. Marks approval-pending entries older than 24h as stale. Verified: `approvalPending.ts:70 markStale` is an `internalMutation`, comment at line 8 reads "Poller (approval-pending-poller.py) calls add; daily cron calls markStale."

### Overlap / race risk with named Hermes-side MC crons

**RACE 1 (the key risk, CONFIRMED): `approval_pending_mark_stale` (Convex) vs `MC Approval Pending Mark Stale` (Hermes job `72ef09a5f670`).**
- Convex job: daily 12:00 UTC, calls `internal.approvalPending.markStale`.
- Hermes job: daily 13:00 UTC cron (`0 13 * * *`), enabled=True, drives the same stale-marking operation via a skill-driven agent prompt.
- These are the SAME logical operation on the SAME `approvalPending` table, scheduled one hour apart by two different schedulers.
- Risk severity: P2. It is not a corruption race because `markStale` is idempotent (it only flips already-old rows to stale). But it is dead duplication: two systems own one invariant. If the Hermes agent prompt drifts (e.g. it starts also resolving or deleting), the two paths diverge and there is no single owner. The Convex internalMutation is the cleaner, cheaper, deterministic owner. The Hermes cron is an LLM agent doing a job a one-line mutation already does for free every day. **This is the textbook "external supervision bolted onto a subsystem that already does the work" anti-pattern, in miniature.**

**NON-RACE (cleared): `grant_review_backstop` vs the Hermes grant-review flow.**
- These are intentionally complementary, not duplicate. Per `reviewActions.ts` and AGENTS.md, the primary path is event-driven: `tasks.updateStatus` fires `requestGrantReview` when a card flips to `in_review`. The Convex `grant_review_backstop` cron is the BACKSTOP that catches cards the event path missed. The Hermes side consumes the resulting webhook (`convex.task.in_review`); it does not independently sweep `in_review`. Both guard with `status === "in_review" && archived !== true`. This is correct belt-and-suspenders design, not a race. APPROVED.

**NON-RACE (cleared): `MC Drift Watchdog` (Hermes job `304ef8d45ac9`, hourly).**
- Its job is to detect prod/dev Convex split (the Anti-Pattern #2 ghost). It reads Convex; it does not write the tables the Convex crons write. No overlap with any of the six. Different concern entirely. APPROVED.

**LOW-RISK NOTE: `soak_auto_flip` (Convex, 15 min) vs `Verify soak_auto_flip (Day 1 shadow)` (Hermes job `d4ad5368852a`, daily 6am).**
- The Hermes job is a shadow VERIFIER (read-only assertion that the Convex flip is firing), per the soak-audit-split plan. Not a competing writer. This is the correct monitoring pattern: the executor lives in Convex, the watchdog lives in Hermes. APPROVED. One housekeeping note: "Day 1 shadow" implies a soak that should have a defined end date. If soak_auto_flip has been live for weeks, this shadow verifier is a candidate for retirement under `cron-retirement-soak-gate`. Flag, do not act.

**STRUCTURAL OBSERVATION:** Convex crons have NO failure signal reaching the operator. If `refreshPrimaryCalendarInternal` throws every 15 min, the only evidence is in the Convex dashboard logs. There is a `MC Authed Convex Cron Liveness Check` (Hermes job `116b63066d80`, weekly Mon 10:00) that positively asserts liveness, which partially covers this, but weekly is too coarse for a 15-min job. Against the monitoring standard (success signal, failure signal within 5 min, alerting path, self-heal), the Convex crons have success and a weak weekly liveness assert, but no sub-5-min failure signal and no alerting path. P2 monitoring gap.

---

## SURFACE 2: GBRAIN AUTOPILOT DAEMON vs THE 19 EXTERNAL GBRAIN CRONS

### What the daemon actually is (verified on disk, `ps aux`)

A live process: `bun gbrain autopilot --repo /Users/TJ/hermes-workspace/Lex-Workspace/wiki`, PID 41645, running since 09:30 today. Plus a sidecar `gbrain jobs work --max-rss 10240` (PID 47970) and the `gbrain serve --http --port 8787` MCP/HTTP server (PID 44225, up since Sunday). Postgres (pgvector) backs it.

`gbrain --help` confirms the daemon's native surface. The autopilot is a "Self-maintaining brain daemon" that runs an internal cycle. The native phase set, per `gbrain dream` help and the autopilot lockfile model, is:
**lint -> backlinks -> sync -> synthesize -> extract -> extract_facts -> resolve_symbol_edges -> consolidate.** `gbrain doctor` is the native health check (resolver, skills, pgvector, RLS, embeddings). `gbrain health` is the native dashboard. `gbrain dream` runs the overnight maintenance cycle ONCE, and its own help text says: "See also: autopilot --install (continuous daemon)."

**Read that again. The native tooling itself tells you the daemon already does this work continuously. Every external cron that re-runs a native phase is re-deriving work the daemon owns.**

### The 19 external GBrain crons and their redundancy verdict

Enumerated from `jobs.json` (86 total jobs; the GBrain-family subset):

REDUNDANT or PARTIALLY REDUNDANT with native autopilot/doctor:

- **GBrain Native Dream (`cb7ae79a89ad`, nightly 2am, ENABLED)** , runs `gbrain dream` (the exact native cycle). Its own description admits it "Shares the autopilot global lockfile, so it cleanly skips if the 300s autopilot cycle is mid-run." So you have a daemon running the cycle continuously AND a cron running the same cycle nightly, coordinating via a lockfile so they do not collide. That lockfile is a tell: it is the patch you write when two schedulers own one job. If autopilot is healthy, this cron is a belt on top of suspenders. KEEP only if the daemon's interval does not guarantee a full nightly cycle; otherwise RETIRE.
- **GBrain Dream Cycle (`a89b3f576c5f`, nightly 2am, DISABLED)** , the retired custom-LLM dream. Correctly superseded by Native Dream. Already off. Good. But it is still in `jobs.json` as a disabled ghost at the same 2am slot, which is clutter, not risk.
- **GBrain Link Rebuild (`7f3e3823db9f`, daily 2:15am, ENABLED)** , runs custom `bun scripts/bulk_link_entities.ts --full` + `export_missing_pages.ts`. This RE-DERIVES the native `backlinks` / `extract links` phase the autopilot runs every cycle. It exists because someone did not trust the native linker to catch sync drift. PARTIALLY REDUNDANT. The honest question: if autopilot's backlinks phase is sound, this is pure re-derivation; if it is not sound, the fix belongs IN gbrain (file an upstream issue), not in a bespoke 2:15am bun script. This is Pillar 1 sprawl.
- **GBrain Native Dream + GBrain Link Rebuild + autopilot daemon** all touch link/edge rebuilding. Three owners for one invariant (mention edges). P2 sprawl.
- **GBrain Daily Health Check (`79f272eaa08b`, 9am, ENABLED)** , runs a bespoke `gbrain-daily-health-check.sh`. Overlaps native `gbrain doctor` / `gbrain health`. The bespoke script may add briefing-file plumbing native doctor lacks, but the health-assessment core is native. PARTIALLY REDUNDANT.
- **GBrain Autopilot Health Audit (`de409bdda8e6`, 11:05am, ENABLED)** , audits the autopilot process health (cycles + errors). This is supervising the self-supervisor. Defensible as an OUTSIDE-the-daemon liveness check (a daemon cannot reliably report its own death), but it overlaps `gbrain doctor`'s scope.
- **GBrain Brain-Growth Audit (`386cfe0cff8b`, 11am, ENABLED)** , growth metrics. Overlaps `gbrain stats` / `gbrain health` deltas. PARTIALLY REDUNDANT with native + with Weekly Score Delta.
- **GBrain Weekly Score Delta (`380d631c83a4`, Sat 7am)** , overlaps Brain-Growth Audit and native `gbrain health`. Two growth-trend reporters.
- **GBrain Weekly Maintenance (`ff7c488f5714`, Mon 6am)** , runs `gbrain health`. Pure native wrapper.
- **GBrain Central-Node Audit (`95cc7457df72`, Mon 9am)** , custom `node audit`. Overlaps native `orphans` / graph-health.
- **GBrain Embed Safety-Net (`5c21b3e4a5c5`, every 15 min, ENABLED)** , `gbrain put`/embed catch-up. RE-DERIVES the native `embed` phase. Native help is explicit: "embed runs on the host as part of the autopilot cycle." A 15-min safety-net for a phase the daemon runs every 300s is suspicious. Either the daemon's embed is unreliable (fix upstream) or this is redundant. P2.

DEFENSIBLE (genuinely external concerns the daemon does NOT own):

- **GBrain Workspace Ingestion (`bd6547019d92`, 4x/day)** , pulls workspace docs into the brain. Source ingestion is a legitimate external trigger.
- **GBrain Morning Briefing (`0efd689bb13c`, 8am)** , produces a human deliverable (briefing). Consumption, not maintenance. Keep.
- **GBrain Nightly Export + Push / GBrain Export Watchdog / GBrain Backup Restore Drill / GBrain Auto-Update Watcher** , export, backup, and binary-update concerns. These are infra OUTSIDE the brain-maintenance daemon's remit. Keep, though Export + Push and Export Watchdog are two crons for one export pipeline (watchdog watches the exporter, acceptable monitoring split).
- **GBrain NER Relationship Extract (`d6a09075016d`, 2:30am)** , a specific extraction the native `extract` phase may not cover. Verify against native `extract <links|timeline|all>` scope before keeping; if native covers it, RETIRE.
- **calendar-to-brain / web-to-brain-enrich / youtube-channel-* / Missing-Link Coverage Harvester** , source-specific enrichment pipelines feeding the brain. External by nature. Keep.

**Core Foxconn finding for Pillar 1:** You are running Garry's self-maintaining brain daemon AND at least 8 external crons (Native Dream, Link Rebuild, Embed Safety-Net, Daily Health Check, Autopilot Health Audit, Brain-Growth Audit, Weekly Score Delta, Weekly Maintenance, Central-Node Audit) that re-run or re-report what the daemon and `gbrain doctor`/`gbrain health` already do natively. The coordination lockfile on Native Dream is the architectural confession. Garry's design intent is ONE daemon that maintains itself and ONE `doctor` that judges it. The Hit Network deployment wrapped that elegant core in a second, hand-built supervision layer because it did not yet trust the native one. Trust is built by fixing the daemon upstream, not by stapling crons to it.

---

## SURFACE 3: PM2 HEALTH

`pm2 list` (verified):
- **mission-control** (id 3) , online, uptime 3h, **restarts 2105**, mem 135.7mb, cpu 0%. `exec_interpreter: /bin/bash`, script `scripts/start-prod.sh`, `autorestart: True`, `unstable_restarts: 0`, `created_at: 2026-06-03T16:23:42Z` (12:23 ET).
- **tandem** (id 1) , online, uptime 15D, restarts 0, mem 31.2mb. Healthy. No concerns. The browser/tandem service is stable.

### The 2105 restarts: NOT cosmetic. A real, recent crash loop.

Evidence from `~/.pm2/logs/mission-control-error.log` (679KB, mtime 15:30 today):
- The script-level circuit breaker fired **177 times today (2026-06-03)**, all between **09:15:00 and 09:44:27 ET**.
- The breaker message: "FATAL: 30 launch attempts within 300s (cap 5). Exiting clean to halt PM2 restart loop. Manual intervention required: investigate, then rm /tmp/mc-restart-attempts and pm2 restart mission-control."
- The `out.log` shows the resolution path: a successful `npm run build` (Next.js 16.2.6, "Compiled successfully", "Ready in 99ms") and the funnel-route assert passing, then the current process came online at 12:23 ET.

Timeline reconstruction:
1. Something this morning left `.next` build artifacts incomplete (the `build_complete()` gate failed; "Build artifacts incomplete" appears 7x in out.log). This is Anti-Pattern #1 (Turbopack cache corruption) / the 2026-05-19 incident class recurring.
2. PM2 `autorestart: True` tried to relaunch repeatedly. The script-level circuit breaker (CB_MAX=5 in CB_WINDOW=300s) caught it and exited 0 every ~10s from 09:15 to 09:44, preventing an infinite tight loop. The breaker WORKED.
3. A rebuild eventually succeeded (manual `pm2 restart` after `rm /tmp/mc-restart-attempts`, per the breaker's own instructions, or an automated recovery), and MC came online at 12:23 and has been stable for 3h.

Verdict on the count: **2105 is the lifetime restart total and it reflects a RECURRING incident class, not a steady-state crash loop.** `unstable_restarts: 0` and a clean 3h uptime confirm MC is NOT crash-looping RIGHT NOW. But 177 breaker fires in a single 30-minute window TODAY proves the underlying fragility (incomplete `.next` artifacts triggering relaunch storms) is live and unresolved. The `start-prod.sh` hardening (C1-C7, circuit breaker, build-complete gate, funnel assert) is genuinely good defensive engineering. It contains the symptom. It does not cure the disease.

**The disease:** `.next` build artifacts go incomplete under some trigger (branch switch, partial build, SIGKILL mid-build, Turbopack cache corruption). Each occurrence costs a restart storm. The cure is to make MC's build artifact production atomic or to detect-and-rebuild OUTSIDE the PM2 restart path (a pre-launch build step that runs once, not per-restart). Right now every relaunch re-checks and potentially re-builds, which is why a single bad-artifact event becomes 30 launch attempts.

Against the incident-response standard: detection is good (breaker logs FATAL), containment is good (clean exit, no infinite loop), but FIX is manual ("Manual intervention required... rm /tmp/mc-restart-attempts and pm2 restart") and there is NO automated alert to the operator when the breaker trips. P1 monitoring gap: MC was effectively DOWN from 09:15 to ~12:23 today (3 hours) and the only signal was a log file nobody was tailing. There must be a breaker-trip alert (Telegram/Discord) wired to the FATAL line.

**SECURITY P1 (out of scope but I will not stay silent):** `pm2 jlist` dumps live secrets into plaintext process env, visible to anyone who can run `pm2 jlist`: `TWILIO_AUTH_TOKEN`, `X_BEARER_TOKEN`, `BFL_API_KEY`, `GOOGLE_CLIENT_SECRET`, `CARTESIA_API_KEY`, `NANSEN_API_KEY`, `KLING_SECRET_KEY`, `COINGECKO_API_KEY` and more on the tandem process. I did not reproduce the values in this report. This is a credential-hygiene finding for whoever owns the tandem ecosystem config. Rotate anything that has appeared in a shared log, and move secrets out of the PM2 ecosystem env into a secrets file the process reads at runtime.

---

## SURFACE 4: WHOLE-SYSTEM / 3-PILLAR INTEGRATION (the most important part)

Step back. The fleet is 86 Hermes crons + 6 Convex crons + 1 GBrain autopilot daemon (with 2 sidecars) + 2 PM2 services + the crontab/launchd layer (other arms). That is at least FOUR independent schedulers driving one organism.

### Pillar 1 (Brain / GBrain): self-supervising core, externally over-supervised.
Covered in Surface 2. Garry's design = one daemon + `doctor`. Hit Network = daemon + ~8 supervision crons. The pillar is sound; the application wrapped it in a redundant second layer. Net: the Brain pillar works, but it is heavier than Garry's stack by roughly the weight of those 8 crons.

### Pillar 2 (Skills): mostly clean, but the proposer/consolidator loop overlaps SIE.
Skills are Garry's skillify/skill-pack model. The native surface (`gbrain skillify`, `gbrain skillpack`, `gbrain skillopt`, RESOLVER.md dispatch) is present. The risk is the boundary with Pillar 3: `sie-skillify-weekly` (Hermes, Tue 10am) and native `gbrain skillify` are two routes to the same skill-extraction outcome. Who owns skill creation, the SIE cron or the native skillify? Undefined ownership.

### Pillar 3 (SIE / Self-Improvement Engine): this is where the sprawl lives.
~20 SIE/routing crons, all ENABLED, verified in `jobs.json`:
sie-d1-daily, sie-d2-weekly, sie-f-mirror, sie-f-audit, sie-scorecard-weekly, sie-improvement-proposer-daily, SIE Self-Inventory v2, sie-learnings-compaction-weekly, sie-pin-audit-weekly, sie-skillify-weekly, sie-promote-token-cleanup, sie-proposer-staleness-alarm, SIE Ingest Source Health, plus the routing-intel family (routing-digest-weekly, routing-intel-synthesis-weekly, routing-intel-queue-daily, routing-intel-verdict-hourly, routing-intel-morning-digest) and dispatch-coverage-daily/weekly.

That is roughly a quarter of the entire 86-job fleet dedicated to the system improving and auditing itself. The honest question the task asks: **is SIE producing value or is it itself the sprawl?** My read: it has become sprawl. Evidence:
- **A staleness-alarm watching a proposer (`sie-proposer-staleness-alarm`) watching the system.** When you need a cron to alarm that your improvement-proposer cron has gone stale, the improvement layer has grown a supervision layer of its own. That is sprawl supervising sprawl.
- **Triple-overlap on "propose work":** SIE improvement-proposer (Pillar 3) + MC Feature Suggester / Cal nightly proposer + Overnight Dreamer all propose cards/features/improvements to the board. The task explicitly named this risk and it is real. Three proposers feeding one board with no dedup contract means the board accrues near-duplicate proposal cards.
- **Triple-overlap on "manage skills":** SIE skillify (propose skills) + native gbrain skillify + a curator/consolidation function (skill consolidation) all touch the skill inventory. Propose + consolidate with no single arbiter = churn.
- **Routing-intel runs FIVE crons** (queue daily, verdict hourly, synthesis weekly, digest weekly, morning digest) to manage agent routing. Hourly verdict + daily queue + 3 weekly/daily reporters for routing decisions is a heavy apparatus.

### Where the same job exists in two (or three) pillars
- Skill creation: Pillar 2 (native skillify) AND Pillar 3 (sie-skillify-weekly).
- Self-inventory/health: Pillar 1 (gbrain doctor/health) AND Pillar 3 (SIE Self-Inventory v2, sie-scorecard).
- Card/feature proposal: Pillar 3 (sie-improvement-proposer) AND Dreamer AND Feature Suggester.
- Stale-marking: Convex (Pillar-agnostic infra) AND Hermes MC Approval crons.

### What Garry's stack would do differently (the elegance standard)
Garry's GStack/GBrain elegance is "the system maintains itself with the fewest moving parts that still close the loop." Concretely:
1. **One scheduler of record per concern.** Convex owns DB-invariant maintenance (stale-marking, archiving, soak-flip). GBrain autopilot owns brain maintenance. Hermes crons own ONLY things neither native layer can do (human deliverables, cross-source ingestion, outside-the-daemon liveness). Today four schedulers overlap on shared concerns.
2. **Trust the native self-supervision.** `gbrain doctor --remediate --yes --target-score 90 --max-usd 5` is a ONE-COMMAND self-healing loop that walks a dependency-ordered plan and refuses to overspend. That single native command can replace the bespoke Daily Health Check + Autopilot Health Audit + Brain-Growth Audit + Link Rebuild + Embed Safety-Net cluster. Garry shipped the self-improvement engine INSIDE the brain. Hit Network rebuilt a parallel one in cron-space (Pillar 3 SIE) on top of it.
3. **One proposer, one arbiter.** Garry's pattern is a single improvement loop with a cost cap and a clear gate, not three independent proposers racing to fill a board. Collapse Dreamer + Feature Suggester + SIE proposer into one proposer with a dedup gate, or give each a non-overlapping lane.
4. **Fewer alarms, deeper.** A staleness-alarm-on-a-proposer is a smell. Garry-level systems have one health surface (`doctor`) that judges everything, not N watchdogs each watching one cron.

**Net 3-pillar read:** Pillars 1 and 2 are sound (they are Garry's actual designs). Pillar 3 (SIE), the "inspired by" pillar, is where the architecture diverged from elegance into accretion. The self-improvement engine is improving the system's PROCESS metrics while measurably adding to the system's WEIGHT and its number of independent failure surfaces. The mandate is "improve as a whole without degrading." SIE in its current form is a net drag on whole-system simplicity even if each individual cron is locally useful. That is the classic self-improvement trap: a self-improver that does not also self-CONSOLIDATE grows monotonically.

---

## HONEST RISKS

1. **The MC crash-loop disease is unresolved.** It WILL recur. Next time the operator may not be watching the log, and there is no breaker-trip alert. P1.
2. **Four schedulers, no single map.** This audit is the first time (per the 6-arm structure) anyone has cross-referenced Convex crons against Hermes crons against the daemon. Nobody owns the union. That is how `approval_pending_mark_stale` ended up doubled.
3. **SIE consolidation has no owner.** The system proposes, audits, and skillifies itself but has no cron whose job is to RETIRE redundant crons. Retirement is the missing half of self-improvement. The `cron-retirement-soak-gate` and `agent-retirement-audit` skills exist; they are not wired to a recurring sweep.
4. **Disabled-ghost clutter in jobs.json.** Retired crons (e.g. `GBrain Dream Cycle` a89b...) linger disabled, inflating the apparent fleet size and confusing future audits.
5. **Convex crons have no sub-5-min failure signal.** A 15-min calendar refresh could be failing for days, surfaced only weekly.
6. **Secret leakage via pm2 jlist.** P1 credential hygiene (Surface 3).
7. **I did NOT independently verify the autopilot daemon's internal cycle interval** (whether it guarantees a full nightly cycle), so the "Native Dream is redundant" call is conditional on that. If the daemon's `--interval` does not guarantee a nightly full cycle, Native Dream is justified. Verify before retiring it. I would not stake my reputation on retiring Native Dream without that one check.

---

## REQUIRED CHANGES (kept separate from suggested)

- **R1 (P1):** Wire a breaker-trip alert. The `start-prod.sh` FATAL line must page the operator (Telegram/Discord). MC was down ~3h today silently.
- **R2 (P1):** Rotate any secret that has appeared in `pm2 jlist`/shared logs; move PM2 ecosystem secrets to a runtime-read secrets file.
- **R3 (P2):** Pick ONE owner for approval-pending stale-marking. The Convex `internalMutation` is the correct owner. Retire the Hermes `MC Approval Pending Mark Stale` cron (after confirming the Convex path covers the full intent).

## SUGGESTED CHANGES

- **S1:** Cure the `.next` incomplete-artifact disease (atomic build, or build-once-before-launch outside the PM2 restart path).
- **S2:** Run `gbrain doctor --remediate` evaluation. If it covers the bespoke health cluster, retire Daily Health Check + Autopilot Health Audit + Brain-Growth Audit + Embed Safety-Net + Link Rebuild in favor of the native loop. Verify daemon interval first (Risk 7).
- **S3:** Collapse the three proposers (Dreamer, Feature Suggester, SIE proposer) into one with a board-dedup gate, or assign non-overlapping lanes.
- **S4:** Add a recurring cron-RETIREMENT sweep (wire `cron-retirement-soak-gate` + `agent-retirement-audit` to a cadence). Self-improvement without self-consolidation is monotonic sprawl.
- **S5:** Add a sub-5-min failure signal + alert path for the Convex crons (or accept the weekly liveness check as sufficient for the daily jobs, but tighten coverage for the 15-min jobs).
- **S6:** Garbage-collect disabled ghost crons from jobs.json.
- **S7:** Establish a single SCHEDULER MAP doc: one table, every job, which of the 4 schedulers owns it, what invariant it owns, so the next overlap is caught at design time.

---

## SKILL-ROUTING AUDIT (mandatory on every review)

The compiled prompt injected the correct skill set for this task class: `gstack-investigate`, `cron-liveness-audit-positive-assertion`, `cron-retirement-soak-gate`, `audit-integration-surface-before-patching`, `agent-retirement-audit`. Routing is NOT broken for this audit. One lesson worth codifying: there is no skill for "cross-scheduler overlap detection" (Convex vs Hermes vs daemon vs crontab). This audit found a duplicate precisely because four schedulers were cross-referenced for the first time. **Proposed new skill: `multi-scheduler-overlap-audit`**, the lesson being "when N independent schedulers drive one system, the union must have a single owner-map or duplicates accrue silently." This belongs in the shared skill layer, not in any one agent file, because every future fleet audit needs it.

---

## PROOF OF COMPLETION

- File written: `/Users/TJ/.hermes/hermes-agent/tasks/plans/scheduler-audit-arm-c-convex-pillars.md`
- Evidence sources (all read live this session, nothing changed):
  - `convex/crons.ts` (6 registrations, read in full)
  - `convex/approvalPending.ts:70`, `convex/reviewActions.ts:425`, `convex/tasks.ts:513` (function existence verified via grep)
  - `~/.hermes/cron/jobs.json` (86 jobs enumerated; enabled-flags verified)
  - `pm2 list` / `pm2 jlist` / `pm2 describe mission-control` (2105 restarts, unstable_restarts 0, 3h uptime)
  - `~/.pm2/logs/mission-control-error.log` (177 breaker fires today, 09:15-09:44 ET)
  - `~/.pm2/logs/mission-control-out.log` (rebuild + recovery trail)
  - `scripts/start-prod.sh` (circuit-breaker + build-gate hardening, read in full)
  - `ps aux` (autopilot PID 41645, jobs-work PID 47970, serve PID 44225)
  - `gbrain --help` / `gbrain dream` help (native phase + daemon equivalence)
  - MC git working tree confirmed: this audit added/changed NOTHING in the repo.

---

## LEARNINGS

1. **The lockfile is the confession.** When two schedulers coordinate via a shared lockfile to avoid colliding on one job (GBrain Native Dream + autopilot), that lockfile is documentation that the job has two owners. The elegant fix is one owner, not a better lock.
2. **A circuit breaker that requires manual reset is containment, not a cure.** `start-prod.sh` is excellent defensive code, and it masked a 3-hour outage today because the breaker's recovery step ("Manual intervention required") had no alert attached. Defensive code without an alert path converts a loud crash into a silent outage. Always pair a breaker with a page.
3. **Restart counters are forensic, not cosmetic.** 2105 looked like a stale counter; the error log proved 177 fires in one 30-minute window today. Never dismiss a high restart count without reading the timestamped log. `unstable_restarts: 0` + high lifetime count = recurring-incident scar, not current loop.
4. **Self-improvement without self-consolidation is monotonic growth.** Pillar 3 (SIE) proposes, audits, skillifies, and alarms, but nothing retires. A self-improving system needs a self-pruning counterpart or it accretes into sprawl. This is the single most important whole-system lesson: the missing cron is the one that DELETES other crons.
5. **Trust the native self-supervision before building a parallel one.** Garry shipped `gbrain doctor --remediate` (a costed, dependency-ordered self-heal loop) inside the brain. Hit Network rebuilt an equivalent in cron-space. The elegant move is to fix the native loop upstream when it is insufficient, not to staple an external supervision layer onto a subsystem that already supervises itself. This is the Foxconn pattern, named.
6. **Multi-scheduler systems need an owner-map skill.** Four independent schedulers (Convex, Hermes cron, GBrain daemon, crontab/launchd) with no union map will accrete duplicate invariants silently. Proposed `multi-scheduler-overlap-audit` skill.
