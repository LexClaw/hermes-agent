# Debate Safety Position: Scheduler Consolidation

Done = the synthesizer has a ranked safety case, mandatory guardrails, explicit pushback against unsafe elegance, and a sequencing plan that improves the scheduler fleet without repeating the recent blind-subtraction regression.

## Position

I am not arguing against consolidation. I am arguing against unsafe consolidation.

The evidence base supports the elegance thesis at the structural level: the fleet is too heavy, has too many scheduler surfaces, and has many watchers re-deriving native health from systems that already expose it. But the recent safety context changes the burden of proof. A blind subtraction 4 days ago cut skill injection by about 72 percent and broke dispatch quality. Mission Control then silently crash-looped for roughly 3 hours today, with the circuit breaker writing a FATAL log but no page reaching the operator. The system has already shown that subtraction and silent supervisor failure can hurt the user.

My clear position: consolidate only after instrumentation. Every retirement must be preceded by owner metadata, output contracts, positive liveness, shadow parity, rollback records, and an independent dead-man path for any supervisor that becomes the watcher of watchers. The first deliverable is not fewer jobs. The first deliverable is a trustworthy map and alert surface.

## Evidence base read

Read in full:

- `/Users/TJ/.hermes/hermes-agent/tasks/plans/addition-by-subtraction-lex-arm.md`
- `/Users/TJ/.hermes/hermes-agent/tasks/plans/addition-by-subtraction-grant-arm.md`
- `/Users/TJ/.hermes/hermes-agent/tasks/plans/addition-by-subtraction-grant-gpt55-arm.md`
- `/Users/TJ/.hermes/hermes-agent/tasks/plans/scheduler-audit-arm-a-jobsjson.md`
- `/Users/TJ/.hermes/hermes-agent/tasks/plans/scheduler-audit-arm-b-shadow.md`
- `/Users/TJ/.hermes/hermes-agent/tasks/plans/scheduler-audit-arm-c-convex-pillars.md`

Key cited facts:

- Lex arm: 86 crons, 345 skills, 28 guard/watchdog/audit/monitor-shaped crons, and the correct diagnosis that the root cause is no retirement or pruning loop.
- Grant arm: 85 enabled Hermes jobs, 28 guard crons, 122 Hit Network skills, the subtraction mandate from 2026-05-30 never landed, and the recent prompt compiler regression cut skill injection about 72 percent.
- GPT-5.5 arm: 86 Hermes jobs, 22 system crontab active lines, 35 launchd jobs, 345 skill files, 122 Hit Network skills, and a need for owner/output/alert/rollback metadata before deletion.
- Arm A: jobs.json has 86 jobs, 57 no_agent script jobs, 29 LLM-agent jobs, 55 producers, 31 guards, 83 ok, 1 error, 2 never-run, 1 paused. Main shape is fragmentation, not obvious mass dead weight.
- Arm B: crontab plus launchd has 22 crontab lines and 35 active plists; at least 6 double-schedules or cross-surface duplicates, including memory_distill double-firing from two script copies and task_index_sync double-firing while broken.
- Arm C: Convex has 6 crons, GBrain autopilot is live, PM2 has mission-control online but with 2105 lifetime restarts, and MC had 177 breaker fires between 09:15 and 09:44 ET today with no operator alert.

## Ranked risk register

### P0: Consolidated supervisor becomes a silent single point of failure

- Consolidation target: Cron scheduler safety supervisor, GBrain supervisor, MC supervisor, SIE or routing supervisor.
- What breaks: multiple independent guards become one supervisor. If that one script fails, misroutes alerts, loses credentials, or silently stops writing, every failure class it absorbed becomes invisible.
- User-visible impact: scheduler failures, stale GBrain, MC board drift, or broken dispatch coverage continue for hours or days with no warning.
- Evidence: Lex arm explicitly notes the risk of one supervisor failing where 4 independent watchers had redundancy. Grant arm calls this the most dangerous moment. Arm A warns that consolidating guards creates a SPOF. Arm C proves the pattern with MC: the circuit breaker contained a restart storm but no alert reached the operator, causing a silent 3-hour outage.
- Safety position: no N-to-1 watcher retirement until the new supervisor has positive-assertion liveness and an external dead-man that is not monitored by itself.

### P0: Blind subtraction removes load-bearing defense-in-depth

- Consolidation target: scheduler guards, skill corpus, prompt compiler defaults, GBrain maintenance jobs, SIE coverage jobs.
- What breaks: a guard that looks redundant is actually the only detector for a past incident class, or a prompt/skill pruning change removes borderline but necessary context.
- User-visible impact: dispatches degrade, skills do not load, review coverage drops, stale paths or missing outputs go unnoticed.
- Evidence: Grant arm documents the 2026-05-30 subtraction attempt that changed live matcher defaults from `relevance_floor 0.4` to `0.6` and `top_n 25` to `7`, injecting about 72 percent fewer skills and breaking dispatch quality. Arm A says scheduler guards exist partly because scheduler deletion broke dispatches recently.
- Safety position: no deletion by count target. Every proposed retirement must prove output parity in shadow mode and include prompt-compile or selector regression tests where skill routing is affected.

### P1: Mission Control outage class recurs silently

- Consolidation target: MC health, PM2 restart handling, Convex/Hermes MC cron ownership.
- What breaks: `.next` artifacts become incomplete again, PM2 loops, the script-level circuit breaker halts restarts, and no alert fires.
- User-visible impact: Mission Control is down or stale for hours. The operator finds it only by noticing missing behavior or manually reading PM2 logs.
- Evidence: Arm C reconstructs a real incident today: 177 breaker fires from 09:15 to 09:44 ET, MC effectively down until around 12:23 ET, no page. Arm C requires a breaker-trip alert as R1.
- Safety position: MC alerting is not optional and must ship before MC consolidation. A supervisor that silently reports green while MC is down is worse than today.

### P1: Cross-scheduler duplication persists or is retired in the wrong direction

- Consolidation target: crontab, launchd, jobs.json, Convex crons, GBrain autopilot, PM2.
- What breaks: one logical invariant remains double-owned, or the wrong owner is retired because the plan looked only at one scheduler surface.
- User-visible impact: duplicate writes, race windows, noisy logs, stale cards, broken memory outputs, or invisible failures.
- Evidence: Arm B found at least 6 cross-surface duplicates or double schedules. memory_distill fires 14 times/day across cron and launchd from two script copies. memory-auto-indexer double-fired one second apart. task_index_sync double-fired while broken every run. Arm C found Convex `approval_pending_mark_stale` and Hermes `MC Approval Pending Mark Stale` both own the same operation one hour apart.
- Safety position: no retirement decision from a single-surface audit. The union owner map must cover jobs.json, system crontab, launchd, Convex crons, daemon loops, and PM2.

### P1: Native health surfaces are trusted beyond their actual coverage

- Consolidation target: GBrain external health jobs into `gbrain doctor` and autopilot.
- What breaks: the native surface omits a check currently covered by a bespoke watcher, such as export freshness, central-node shape, backup restore, source-specific ingestion, or a specific extraction.
- User-visible impact: brain health appears good while a downstream artifact stops updating or a source pipeline stalls.
- Evidence: Grant GPT-5.5 arm notes `gbrain doctor --fast --json` skipped DB checks in the observed run, recommending fast doctor for frequent checks and full doctor for slower checks. Arm C says Native Dream redundancy is conditional because autopilot interval coverage was not independently verified. Arm C also classifies backup, export, source ingestion, and human deliverables as defensible external concerns.
- Safety position: consume native surfaces where they cover the invariant, but verify coverage category by category. Keep external checks for concerns outside the daemon.

### P1: Consolidating producers increases blast radius

- Consolidation target: SIE, routing intel, Meet EA, memory DAG, GBrain ingestion, MC exports.
- What breaks: multiple small producer jobs become one large pipeline. A single pipeline bug blocks every stage, whereas today a failure can be isolated.
- User-visible impact: no meeting brief, no transcript filing, no action extraction, no routing digest, no SIE ingest, or no memory generation.
- Evidence: Arm A distinguishes 55 producers from 31 guards and warns that consolidating producers increases blast radius. Arm B says the memory cluster needs one sequenced DAG, not all stages crammed into a racing window. Arm A says Meet EA is a pure consolidation candidate only if latency and output parity pass.
- Safety position: guard consolidation can be earlier than producer consolidation. Producer consolidation requires per-stage state, per-stage retry, and per-stage output contracts.

### P1: Convex cron failures remain invisible

- Consolidation target: MC/Convex ownership and liveness.
- What breaks: Convex scheduled functions fail, but the only evidence is in Convex dashboard logs or a weekly liveness check.
- User-visible impact: calendar refresh, stale agent activity expiry, soak auto-flip, grant review backstop, decision queue archive, or approval pending stale marking fail without prompt awareness.
- Evidence: Arm C says Convex crons have no sub-5-min failure signal and only weak weekly liveness via `MC Authed Convex Cron Liveness Check`.
- Safety position: moving ownership into Convex is correct for DB invariants, but only with failure signal and alert path. Deterministic execution without alerting is not operational safety.

### P1: The subtraction engine becomes another sprawl engine

- Consolidation target: new `subtraction-engine`, prune proposer, retirement loop.
- What breaks: the anti-overengineering fix creates yet another weekly report, card generator, taxonomy, and watcher, increasing load without retiring anything.
- User-visible impact: more cards about cards, more monitors watching monitors, and no reduction in operational risk.
- Evidence: Lex arm proposes a weekly prune proposer. Grant arm pushes a smaller Phase 0: one drift-audit bullet first, then consider a proposer only after it earns promotion. Arm C identifies SIE as a self-improver that grew monotonically because it lacked self-consolidation.
- Safety position: start flag-only inside an existing drift audit, with candidate reports and no mutation. Promote to a standing engine only after it produces useful, approved retirements.

### P2: Grep-confirmed orphan is mistaken for dead code

- Consolidation target: scripts, skills, launchd plists, crontab lines, jobs.json entries.
- What breaks: a script not found by a simple grep is shell-invoked, referenced via a shim, used as a pattern, or alive under a different path/name variant.
- User-visible impact: a live pipeline disappears, or a recovery pattern is lost.
- Evidence: Grant arm warns grep-confirmed orphan is not proof of death. Arm B shows name variants and path variants matter: memory_distill uses two different script copies, memory health has hyphen and underscore variants, and ale_recommendations is actually dead only after `find` and logs proved the file absent.
- Safety position: death requires negative evidence across all invocation paths plus log/PID/output checks, not grep alone.

### P2: Disabled ghosts and shadow verifiers inflate counts and confuse future audits

- Consolidation target: disabled jobs and temporary shadow checks.
- What breaks: audit counts overstate active fleet size, or a temporary verifier stays forever and becomes permanent scaffolding.
- User-visible impact: future agents chase stale jobs or miss the actual live risk.
- Evidence: Arm A marks `GBrain Dream Cycle` as paused legacy. Arm C flags `Verify soak_auto_flip (Day 1 shadow)` as read-only and probably should have a defined end date.
- Safety position: ghosts should be archived through a documented recovery window, not left in active config forever.

### P2: Legacy crontab is drained without replacing observability

- Consolidation target: 22 system crontab lines.
- What breaks: a raw cron job is removed or migrated without logs, owner, success signal, or rollback.
- User-visible impact: ingestion, memory, email-to-brain, security, skill-check, or heartbeat jobs stop quietly.
- Evidence: Arm B says crontab is the unaudited legacy layer but many jobs are alive. The voice watchdog writes to `/dev/null`, so it is alive only by proxy. Several launchd jobs have non-zero last exits with no alert path.
- Safety position: drain crontab one job at a time, with direct liveness evidence and new-governance proof before old surface is quieted.

### P2: Security risk remains outside the consolidation plan

- Consolidation target: PM2 and service governance.
- What breaks: secrets remain exposed in PM2 environment dumps or shared logs.
- User-visible impact: credential compromise, service abuse, forced rotation under pressure.
- Evidence: Arm C flags PM2 `jlist` exposing live secrets in plaintext process env and requires rotation/moving secrets out of PM2 ecosystem env.
- Safety position: not part of scheduler consolidation, but no master plan should ignore it because PM2 is one of the scheduler/runtime surfaces being governed.

### P2: SIE, Dreamer, and Feature Suggester continue producing duplicate work

- Consolidation target: SIE/routing/proposer layer.
- What breaks: three proposer loops keep feeding near-duplicate cards into MC while consolidation focuses only on watchdogs.
- User-visible impact: board clutter, wasted agent cycles, repeated proposals, and slower operator triage.
- Evidence: Arm C identifies triple-overlap on card/feature proposals: SIE improvement proposer, MC Feature Suggester, and Overnight Dreamer. Grant GPT-5.5 arm identifies SIE and routing as about 20 jobs.
- Safety position: assign non-overlapping lanes or consolidate behind a dedup gate, but do not remove proposal paths until their outputs are compared.

### P3: Dashboard count reduction becomes the goal instead of capability preservation

- Consolidation target: all surfaces.
- What breaks: the plan optimizes for fewer crons or fewer skills rather than fewer failure modes.
- User-visible impact: attractive architecture diagram, worse operations.
- Evidence: Lex arm says the fix is not delete watchdogs, it is collapse N overlapping watchers into one supervisor where capability is preserved. Grant arm says the number should go down as a consequence, not as the goal.
- Safety position: success metric is coverage parity plus fewer independent owners, not raw count.

## Mandatory guardrails before any consolidation ships

### Universal guardrails

These apply to every consolidation and every retirement.

1. Versioned snapshots before change:
   - Snapshot `~/.hermes/cron/jobs.json`.
   - Snapshot `crontab -l`.
   - Snapshot launchd plist inventory and `launchctl list` state.
   - Snapshot Convex cron registrations.
   - Snapshot PM2 process list and restart counters.
   - Snapshot skill manifest with active, archived, vendored, pinned, and prunable labels.

2. Owner map:
   - Every job must have one owner.
   - Every invariant must have one scheduler of record.
   - If a job remains outside the scheduler of record, it needs an owner and reason.

3. Output contract:
   - Durable artifact, DB mutation, alert, queue drain, page, card, or heartbeat must be named.
   - Silent-when-healthy jobs still need a success heartbeat somewhere observable.

4. Alert contract:
   - Failure signal within 5 minutes for user-facing or safety-critical systems.
   - Explicit alert destination, severity, and dedup behavior.
   - No more log-only FATAL events for MC or scheduler liveness.

5. Positive-assertion liveness:
   - Healthy runs emit a heartbeat row or state file.
   - Silence is treated as failure.
   - Last successful run, last failure, and last output must be inspectable.

6. Shadow parity:
   - New supervisor runs side-by-side with old jobs for at least 7 days unless the job cadence requires longer.
   - Per-subcheck comparison proves every old alert class is reproduced or intentionally dropped with approval.
   - No old job is disabled until parity is documented.

7. External dead-man for watcher-of-watchers:
   - The cron scheduler safety supervisor cannot monitor only itself.
   - It needs an independent liveness path, such as launchd or another minimal external check.
   - If that dead-man alerts on silence, it must not depend on the same broken scheduler path.

8. Rollback record:
   - For each retirement, store old schedule, command, env, output path, owner, reason, and restore command.
   - Disable or pause before delete.
   - Keep a recovery window after pause.

9. One cluster at a time:
   - Do not consolidate GBrain, cron safety, MC, SIE, and crontab in one batch.
   - A bad consolidation must have small blast radius and clear attribution.

10. Human approval for actual retirement:
   - The subtraction loop proposes and proves.
   - TJ approves actual removal.
   - No auto-delete.

### Guardrails by consolidation cluster

#### Cron scheduler safety supervisor

Mandatory before retiring any of the four current cron safety jobs:

- Subchecks must cover missed runs, heartbeat gap, jobs.json shrink, and stale paths.
- Supervisor must run in shadow for 7 days with current four guards still enabled.
- Each subcheck must emit healthy and failed state.
- External dead-man must alert if the supervisor itself misses cadence.
- Jobs.json shrink detection must remain P0/P1 severity because blind registry loss can break dispatches.
- Do not merge this first unless MC alerting is already working, because this is the highest SPOF consolidation.

Cited basis: Lex arm, Grant arm, Arm A.

#### GBrain supervisor

Mandatory before retiring external GBrain health jobs:

- Verify `gbrain doctor --json`, `gbrain doctor --fast --json`, `gbrain health`, autopilot logs, and daemon interval coverage.
- Build a coverage matrix for native doctor vs each current external watcher.
- Keep backup restore drill separate unless native tool proves restore, not just health.
- Keep source ingestion and human deliverables separate from maintenance health.
- Treat Native Dream retirement as conditional until autopilot guarantees a full nightly cycle or equivalent.
- Keep external liveness for daemon death, because a daemon cannot reliably report its own death.

Cited basis: Grant GPT-5.5 arm, Arm C.

#### Mission Control and Convex supervisor

Mandatory before MC consolidation:

- Wire breaker-trip alerts for `start-prod.sh` FATAL lines.
- Fix or isolate `.next` incomplete-artifact recurrence with atomic build or build-once-before-launch outside the PM2 restart loop.
- Pick Convex as owner for DB-invariant crons where applicable, especially approval-pending stale marking, after confirming scope.
- Add sub-5-min failure signal for 15-min Convex jobs, or explicit risk acceptance for lower-criticality jobs.
- Preserve `grant_review_backstop` because Arm C cleared it as complementary defense-in-depth, not duplicate.
- Keep MC drift watchdog coverage, potentially as a subcheck, because it protects a specific prod/dev split incident class.

Cited basis: Arm C, Arm A.

#### Shadow layer: crontab and launchd

Mandatory before draining crontab:

- Retire duplicates only after log mtime proves new owner fires and old owner is quiet.
- Reconcile divergent script copies before choosing a winner, especially memory_distill.
- Fix broken jobs before migrating them, especially task_index_sync PATH and Convex deployment name.
- Keep true daemons on launchd.
- Migrate batch jobs only after they have owner, output, log, and alert contracts.
- Add log path for jobs currently writing to `/dev/null`, especially voice watchdog if it stays in cron.

Cited basis: Arm B.

#### SIE and routing consolidation

Mandatory before collapsing SIE/routing jobs:

- Define lanes for SIE proposer, Dreamer, and Feature Suggester, or put them behind a dedup gate.
- Do not merge red or broken producers. Fix `sie-d1-daily` first.
- Separate producer stages from guard stages.
- For routing, require evidence that queue, verdict, digest, synthesis, and coverage outputs are all reproduced.
- Add a stop condition: if a stage produces only cards about cards for 30 days, it becomes a retirement candidate.

Cited basis: Arm A, Arm C, Grant GPT-5.5 arm.

#### Skill consolidation

Mandatory before any skill pruning:

- Never touch vendored `gstack-*` and `gbrain-*` skills.
- Label active, archived, vendored, pinned, and prunable skills separately.
- Track skill load frequency, downstream correction rate, and prompt-token footprint.
- Run selector regression tests and prompt-compile diff tests before changing corpus or matcher defaults.
- Use Curator-style archive, not delete.
- Keep archived counts out of active-count dashboards.

Cited basis: Lex arm, Grant arm, Grant GPT-5.5 arm.

## Where I push back on the elegance-maximalist

### Pushback 1: Do not consolidate the watcher-of-watchers aggressively

The cron safety layer is not the place to prove aesthetic courage. It is the place to prove operational humility. Four guards may be ugly, but they cover different failure classes: missed runs, heartbeat, stale paths, and jobs.json shrink. Collapse them only after an external dead-man exists. If the elegance plan wants this early, I reject that sequencing.

### Pushback 2: `grant_review_backstop` is real defense-in-depth, not redundant clutter

Arm C cleared this as a non-race. Event-driven review is primary; Convex backstop catches missed event paths and filters archived cards. Removing it because it is another cron would degrade the review system. It can be monitored better, but it should not be retired as duplicate.

### Pushback 3: Mission Control health cannot be simplified before it can page

The MC crash loop today is the clearest warning. The circuit breaker worked as containment, then became silent failure because it had no alert path. Consolidating MC watchers before breaker-trip alerting is backwards.

### Pushback 4: Native GBrain should be trusted only after coverage proof

I agree with the elegance-maximalist that GBrain autopilot plus `doctor` is the intended elegant core. I reject the leap from intended core to immediate retirement of external checks. Backup restore, export freshness, source ingestion, central-node shape, and daemon-death detection are not automatically covered by `doctor`. Coverage matrix first, retirement second.

### Pushback 5: Producer consolidation is not the same as guard consolidation

A supervisor that reports on 8 checks can be simple. A pipeline that owns 8 producer stages can become a new monolith. Meet EA and memory DAG may be good consolidation candidates, but only with per-stage state and retry. Do not hide producer failure inside one green pipeline status.

### Pushback 6: The subtraction engine should start as a discipline, not a factory

A new report-only proposer may be useful. A new self-improvement pillar that files more cards, needs its own staleness alarm, and creates a dashboard is exactly how SIE became sprawl. Start with the missing Sunday drift-audit bullet and a machine-readable report. Promote only after it proves value.

### Pushback 7: Count reduction is not a success criterion

If the plan says 86 becomes 40 without saying which failure classes remain covered, it is unsafe. The correct target is one owner per invariant, parity-proven coverage, and less hidden scheduling. The count should fall as a consequence.

## What must not be touched without stronger evidence

- Vendored upstream `gstack-*` and `gbrain-*` skills.
- True launchd daemons: Hermes gateway, voice server/tunnel/TTS/PTT, GBrain autopilot, GBrain MCP, Postgres, PM2, and similar service processes.
- `grant_review_backstop`, because it is a cleared complementary backstop.
- GBrain backup restore drill, unless native tooling proves restore capability.
- Human deliverables such as GBrain Morning Briefing, unless replaced by a verified user-facing output path.
- MC drift watchdog coverage, though it can become a subcheck.
- Scheduler shrink detection, though it can become a subcheck.
- Any producer that is currently red or never-run until the root cause is resolved. Broken is not retired. Broken is fixed or explicitly decommissioned with proof.

## Safe sequencing

### Phase 0: Freeze and map reality

- Write versioned snapshots for jobs.json, crontab, launchd, Convex crons, PM2, and skill manifests.
- Produce one union scheduler map covering all surfaces.
- Add owner, subsystem, scheduler_of_record, output_contract, alert_contract, rollback_command, and retirement_candidate fields.
- Classify active, archived, vendored, pinned, and prunable skills.
- No retirement in this phase.

Why first: Arm B proved that single-surface audits undercount duplicates. Without a union map, the plan can retire the wrong owner.

### Phase 1: Fix active silent-failure gaps

- Wire MC breaker-trip alert.
- Add alerting or liveness for Convex crons, especially 15-min jobs.
- Fix task_index_sync PATH and Convex deployment name before deciding its long-term owner.
- Investigate `sie-d1-daily` error and never-run jobs.
- Add direct logs where jobs write to `/dev/null` or only have proxy evidence.

Why second: Consolidation should not start from a fleet with known silent failures.

### Phase 2: Ship report-only subtraction discipline

- Add the missing subtraction scan to the existing Sunday drift audit or equivalent recurring review.
- Output candidates only, with rationale and required soak gates.
- Do not add a large new engine until the simple recurring scan proves useful.
- Ensure relevant retirement and liveness skills load for this task type.

Why now: It closes the one-way ratchet without mutating the scheduler.

### Phase 3: Build supervisors in shadow mode, no retirements

Start with the lowest-risk guard consolidations, but do not disable old jobs.

Recommended order:

1. GBrain health supervisor in shadow, because native `doctor` gives a structured base, while keeping producers independent.
2. Cron safety supervisor in shadow only after its external dead-man exists.
3. MC/Convex supervisor once MC breaker alerting is live.
4. Routing/SIE report-mode supervisor after broken SIE jobs are fixed.
5. Meet EA and memory DAG shadow after per-stage state is defined.

Why shadow: It proves coverage without taking away existing defense-in-depth.

### Phase 4: One-cluster pause, soak, and recovery window

- Pause only old jobs whose coverage is fully reproduced.
- Keep recovery record and restore command.
- Observe for one recovery window.
- Retire one cluster at a time.

Why not delete: jobs.json is not a git-tracked safety net in the same way code is, and the recent skill regression shows blind subtraction is dangerous.

### Phase 5: Drain legacy crontab carefully

- Keep true daemons on launchd.
- Move batch jobs to the governed scheduler only after logs and outputs prove the new owner fires.
- Resolve double schedules using Arm B evidence, generally keeping launchd where it already owns periodic or daemon behavior, and jobs.json where batch governance is desired.
- Confirm old crontab entries are quiet before removal.

Why later: the shadow layer has the highest name/path variant risk.

### Phase 6: Skill consolidation after telemetry

- Use Curator and skill telemetry, not raw count.
- Regression-test prompt compiler behavior.
- Archive and soak, do not delete.
- Keep upstream vendored skills out of scope.

Why last: skill pruning caused the recent dispatch breakage. It needs the strongest regression harness.

## Highest-conviction guardrail

The highest-conviction guardrail is positive-assertion liveness plus an external dead-man for every consolidated supervisor, especially the cron scheduler safety supervisor.

I stake my reputation on this. The worst failure mode in the entire plan is not that the old fleet remains ugly. The worst failure mode is that the plan creates one elegant supervisor that silently dies, taking all consolidated visibility with it. MC already demonstrated this exact class today: a breaker stopped a crash loop, but no alert fired, so a contained failure became a silent 3-hour outage. Do not repeat that pattern at the scheduler level.

## Biggest fear if the elegant plan ships as-is

My biggest fear is that the team celebrates a lower cron count while quietly converting distributed, ugly, partly redundant safety into a small number of silent SPOFs.

The user experience would be worse than today: fewer alarms, cleaner diagrams, and longer undetected outages. A GBrain supervisor dies and the brain rots quietly. A cron safety supervisor dies and missed jobs stop being reported. MC breaker trips again and nobody is paged. Skill pruning passes because the active-count dashboard looks better, but the prompt compiler loses borderline-relevant context again. That is addition by subtraction becoming subtraction of safety.

## Debate ask to the synthesizer

Approve consolidation only with these non-negotiables:

- Instrument before retire.
- One owner per invariant before one job per subsystem.
- Positive liveness before fewer watchers.
- External dead-man before watcher-of-watchers consolidation.
- Shadow parity before pause.
- Pause and recovery window before delete.
- Regression tests before skill pruning.
- Human approval before actual retirement.

If the elegance-maximalist accepts those constraints, the plan can become bulletproof. If not, I would reject the aggressive version as unsafe.

## Learnings

- The system does not need a deletion spree. It needs a reversible, observable retirement discipline.
- Cross-scheduler overlap is the central audit unit. jobs.json alone is not the fleet.
- A supervisor without a heartbeat and external dead-man is not simplification. It is hidden blast radius.
- Native health surfaces are valuable, but only after their coverage is mapped against the bespoke checks they replace.
- Recent incidents must set the proof burden. The 72 percent skill-injection regression and silent MC crash loop are not anecdotes. They are the safety constraints for the master plan.
- The cleanest architecture is not the one with the fewest jobs. It is the one where every invariant has one owner, every owner has an output contract, and every failure has an alert path.
