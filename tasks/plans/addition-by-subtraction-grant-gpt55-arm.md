# Addition by Subtraction Audit, Grant GPT-5.5 Arm

Done means a read-only, evidence-backed audit of the Hit Network cron and skill stack exists on disk with concrete counts, concrete examples, root cause, risks, and a phased plan that deletes nothing without later approval.

## Verdict

REJECTED as an architecture shape. APPROVED as a system worth saving by subtraction.

The stack has Foxconn-factory scaffolding, but the root cause is not that individual crons or skills are foolish. The root cause is charter asymmetry: the system has many organs that add, codify, monitor, propose, skillify, and file cards, but only a narrow skill curator that subtracts inside one surface. There is no cross-surface retirement engine that owns recurring-cost reduction across crons, skills, prompts, Mission Control cards, and legacy system crontab.

Result: every incident leaves a scar. Some scars are good permanent knowledge. Too many became permanent watchers, one-off skills, and daily audits that re-derive health already exposed by native surfaces like `gbrain doctor`.

I would stake my reputation on this structural diagnosis.

## Evidence gathered

Commands and files inspected:

- Read compiled prompt: `/tmp/lex-prompts/grant-audit-gpt55.txt`.
- Read Hermes cron source of truth: `/Users/TJ/.hermes/cron/jobs.json`.
- Counted skill files under `/Users/TJ/.hermes/skills`, excluding `.git`.
- Counted Hit Network prunable skills under `/Users/TJ/.hermes/skills/hit-network`.
- Checked system crontab with `crontab -l` because Hermes crons do not appear there.
- Checked GBrain native surfaces with `gbrain health`, `gbrain doctor --help`, and `gbrain doctor --fast --json`.
- Read curator implementation in `/Users/TJ/.hermes/hermes-agent/agent/curator.py`.
- Read latest curator report at `/Users/TJ/.hermes/logs/curator/20260603-144251/REPORT.md`.

Verified counts:

- Hermes cron jobs in `~/.hermes/cron/jobs.json`: 86.
- Enabled Hermes cron jobs: 85.
- Disabled Hermes cron jobs: 1, `GBrain Dream Cycle (Nightly 2am)`.
- Hermes cron last status: 83 ok, 1 error, 2 never run.
- Non-ok Hermes cron: `sie-d1-daily`.
- Never-run Hermes crons: `MC Authed Convex Cron Liveness Check`, `SIE Ingest Source Health (daily 8:15am)`.
- System crontab active lines outside Hermes jobs.json: 22.
- SKILL.md files excluding `.git`: 345.
- Visible active SKILL.md files excluding hidden dirs: 339.
- Hidden archived SKILL.md files under `.archive`: 6.
- Non-hidden top-level skill directories: 127.
- Top-level directories with at least one SKILL.md descendant: 96 visible, 97 including `.archive`.
- Top-level directories with no SKILL.md descendant: 31, examples include `brain-ops`, `briefing`, `citation-fixer`, `data-research`, `templates`, `task-skills-v15-backup`.
- `hit-network` SKILL.md files: 122.
- Vendored or upstream-rooted `gstack-*` skills verified on disk: 45.
- Vendored or upstream-rooted `gbrain-*` skills verified on disk: 9.
- Hit Network skill corpus size: 35,544 lines across 122 skills, average 291.3 lines, median 242 lines.

GBrain health surfaces verified:

- `gbrain health` returned health score 8/10, embed coverage 100.0 percent, missing embeddings 0, stale pages 1974, orphan pages 9086, link coverage 98.9 percent, timeline coverage 51.2 percent.
- `gbrain doctor --help` returned usage, confirming `gbrain doctor` is a native command.
- `gbrain doctor --fast --json` returned schema_version 2, status warnings, health_score 85, category_scores brain 100, skill 90, ops 95, meta 100.

## Findings

### Finding 1: The cron layer has at least 29 guard, watchdog, audit, monitor, health, alarm, check, drift, liveness, stale, safety-net, coverage, or verify shaped jobs

Concrete jobs matching that surface by name:

- `GBrain Daily Health Check (9am)`
- `GBrain Auto-Update Watcher (Daily 4am)`
- `GBrain Brain-Growth Audit (daily 11am)`
- `Cron Health Monitor (every 2h)`
- `Memory Health Check (Daily 3am)`
- `Jobs.json Shrink Alarm (every 30min)`
- `Agent Model Drift Monitor`
- `GBrain Embed Safety-Net (every 15 min)`
- `GBrain Central-Node Audit (weekly, Mon 09:00 ET)`
- `GBrain Export Watchdog (daily 06:00)`
- `GBrain Autopilot Health Audit (daily 11:05am)`
- `mc-healthcheck`
- `sie-f-audit`
- `MC Drift Watchdog (prod/dev split detector)`
- `sie-pin-audit-weekly`
- `dispatch-coverage-daily`
- `dispatch-coverage-weekly`
- `Cron-Heartbeat Watchdog (every 4h)`
- `Meeting Prep Auto-Watcher`
- `Synthesis-Page Staleness Surface (discipline-gap card filer)`
- `Stale Cron Path Watcher (23:55)`
- `MC Stuck in_progress Audit`
- `MC Approval Pending Mark Stale`
- `Verify soak_auto_flip (Day 1 shadow)`
- `Missing-Link Coverage Harvester (07:30 ET)`
- `Meet EA: Calendar Watcher (every 1 min)`
- `sie-proposer-staleness-alarm`
- `MC Authed Convex Cron Liveness Check`
- `SIE Ingest Source Health (daily 8:15am)`

This is Garry's critique almost literally: 29 alarms in the Hermes scheduler alone, before counting 22 legacy system crontab lines.

### Finding 2: The GBrain subsystem is over-supervised despite having native health surfaces

I counted 23 jobs whose primary domain is GBrain or brain maintenance:

- `GBrain Weekly Maintenance (Monday 6am)`
- `GBrain Morning Briefing (8am)`
- `GBrain Workspace Ingestion`
- `GBrain Daily Health Check (9am)`
- `Lex Sunday Review (Self-Assessment + Memory Maintenance, 10 AM)`
- `GBrain Auto-Update Watcher (Daily 4am)`
- `GBrain Weekly Score Delta (Sat 7am)`
- `GBrain Backup Restore Drill (monthly)`
- `GBrain Dream Cycle (Nightly 2am)`, disabled
- `GBrain Link Rebuild (Daily 2:15am)`
- `GBrain Brain-Growth Audit (daily 11am)`
- `Memory Health Check (Daily 3am)`
- `calendar-to-brain`
- `GBrain Embed Safety-Net (every 15 min)`
- `GBrain Central-Node Audit (weekly, Mon 09:00 ET)`
- `web-to-brain-enrich`
- `GBrain Nightly Export + Push`
- `GBrain Export Watchdog (daily 06:00)`
- `GBrain Autopilot Health Audit (daily 11:05am)`
- `Overnight Executor (11pm-6am, board-drainer)`
- `Missing-Link Coverage Harvester (07:30 ET)`
- `GBrain Native Dream (Nightly 2am)`
- `GBrain NER Relationship Extract (nightly 2:30am)`

Overlap examples:

- Health or audit: `GBrain Daily Health Check`, `GBrain Brain-Growth Audit`, `GBrain Autopilot Health Audit`, `GBrain Weekly Maintenance`, `GBrain Weekly Score Delta`, `Memory Health Check`.
- Export: `GBrain Nightly Export + Push` plus `GBrain Export Watchdog`.
- Dream cycle: disabled `GBrain Dream Cycle (Nightly 2am)` still exists next to enabled `GBrain Native Dream (Nightly 2am)`.
- Link maintenance: `GBrain Link Rebuild`, `GBrain NER Relationship Extract`, `GBrain Embed Safety-Net`, `Missing-Link Coverage Harvester`.

The native surface already exists. `gbrain doctor --fast --json` returned structured score and issues. `gbrain health` returned current graph metrics. Multiple crons are re-deriving or second-guessing that health instead of delegating to the native surface.

### Finding 3: Mission Control has a real-time health check plus several adjacent watchdogs

Primary Mission Control jobs counted: 11.

- `mc-nightly-backup (2am)`
- `sync_task_index_from_convex`
- `mc-healthcheck`
- `MC Overnight Reports Collector`
- `MC People Graph Export`
- `MC Drift Watchdog (prod/dev split detector)`
- `MC Feature Suggester (nightly proposer)`
- `MC Stuck in_progress Audit`
- `MC Approval Pending Mark Stale`
- `MC Approval Pending Poller`
- `MC Authed Convex Cron Liveness Check`

Overlap examples:

- `mc-healthcheck` runs every 5 minutes.
- `MC Drift Watchdog (prod/dev split detector)` runs hourly.
- `MC Authed Convex Cron Liveness Check` checks cron liveness weekly.
- `MC Stuck in_progress Audit`, `MC Approval Pending Mark Stale`, and `MC Approval Pending Poller` all police board state.

Some of these are likely load-bearing because Mission Control is a product surface. The elegant shape is not deletion. The elegant shape is one Mission Control supervisor with subchecks, severity routing, and a single deduplicated alert contract.

### Finding 4: SIE and routing are additive by design, but subtraction is not symmetric

Primary SIE and routing jobs counted: 20.

- `sie-d1-daily`
- `sie-d2-weekly`
- `sie-f-mirror`
- `sie-f-audit`
- `sie-scorecard-weekly`
- `sie-improvement-proposer-daily`
- `SIE Self-Inventory v2 (nightly 23:00)`
- `sie-learnings-compaction-weekly`
- `sie-pin-audit-weekly`
- `sie-skillify-weekly`
- `dispatch-coverage-daily`
- `dispatch-coverage-weekly`
- `routing-digest-weekly`
- `routing-intel-synthesis-weekly`
- `routing-intel-queue-daily`
- `routing-intel-verdict-hourly`
- `routing-intel-morning-digest`
- `sie-promote-token-cleanup`
- `sie-proposer-staleness-alarm`
- `SIE Ingest Source Health (daily 8:15am)`

The exact one-way ratchet is visible:

- Additive crons: `sie-skillify-weekly`, `sie-improvement-proposer-daily`, `MC Feature Suggester (nightly proposer)`, `Overnight Dreamer (10:30 PM)`.
- Monitoring crons for the additive layer: `dispatch-coverage-daily`, `dispatch-coverage-weekly`, `routing-intel-verdict-hourly`, `sie-proposer-staleness-alarm`, `SIE Ingest Source Health`.
- Missing symmetric cron: no `subtraction-proposer`, no `cron-consolidation-supervisor`, no `skill-retirement-candidate-harvester` outside the skill curator.

This is the structural accumulation mechanism.

### Finding 5: The skill layer is not uniformly bad, but the prunable surface is still heavy

Verified prunable surface: 122 Hit Network skills.

High-density clusters by name:

- Brain cluster: 19 skills, including `brain-coverage-audit`, `brain-first-lookup`, `filesystem-to-brain-migration`, `gbrain-autopilot-ops`, `gbrain-bulk-ingestion`, `gbrain-dream-cycle`, `gbrain-duplicate-detection`, `gbrain-entity-promotion-audit`, `gbrain-link-rebuild`, `gbrain-link-rebuild-daily`, `gbrain-namespace-cleanup`, `gbrain-recipe-authoring`, `gbrain-relationship-extraction-ops`, `gbrain-telegram-continuous-pass-cron-execution`, `gbrain-timeline-batch-preflight`, `gbrain-weekly-score-delta`, `recover-lost-plans-from-gbrain`, `repo-to-brain`, `verify-brain-state-before-claims`.
- GBrain named cluster: 14 skills.
- Overnight cluster: 6 skills, `overnight-autonomous-orchestration`, `overnight-dreamer`, `overnight-dreamer-execution`, `overnight-executor`, `overnight-wave-dispatch-routing`, `overnight-wave-strategic-execution`.
- Audit cluster: 7 skills, `agent-retirement-audit`, `audit-integration-surface-before-patching`, `audit-upstream-before-major-work`, `brain-coverage-audit`, `canonical-install-audit`, `cron-liveness-audit-positive-assertion`, `gbrain-entity-promotion-audit`.
- Mission Control cluster: 4 skills, `mission-control-board-prod-vs-dev`, `mission-control-engineering`, `mission-control-filing`, `mission-control-integration`.
- Voice cluster: 4 skills, `tts-voice-stack`, `twilio-cloudflared-voice-server-ops`, `voice-out-text-hygiene`, `voice-server-cloudflare-recovery`.
- Verify cluster: 3 skills, `verify-before-negating-external-claims`, `verify-brain-state-before-claims`, `verify-spec-before-claiming-done`.

Line-count hotspots in Hit Network:

- `mission-control-board-prod-vs-dev`: 880 lines.
- `grant-mc-verdict-workflow`: 772 lines.
- `prompt-compiler-operations`: 754 lines.
- `x-article-ingest`: 729 lines.
- `gbrain-recipe-authoring`: 678 lines.
- `mission-control-filing`: 657 lines.
- `localhost-service-tailnet-expose`: 655 lines.
- `verify-brain-state-before-claims`: 647 lines.
- `gbrain-bulk-ingestion`: 637 lines.
- `lex-output-hygiene`: 582 lines.

The issue is not merely count. The issue is retrieval and bias tax. 35,544 Hit Network skill lines compete to steer agents. When a narrow scar loads in the wrong task, it becomes behavior, not just documentation.

### Finding 6: Skill consolidation exists, but only as a skill-local organ

The Curator is real and valuable:

- `agent/curator.py` says it performs background skill maintenance.
- It only touches agent-created skills.
- It never auto-deletes, only archives.
- It runs on a 168 hour interval in config.
- It asks for umbrella-building consolidation.
- Its latest report shows `Agent-created skills: 46 -> 40 (-6)`.
- Latest archived and absorbed skills were:
  - `compiled-truth-people-page` -> `brain-coverage-audit`
  - `historical-db-snapshot-merge` -> `db-merge-consolidation`
  - `mc-verdict-and-dispatch` -> `grant-mc-verdict-workflow`
  - `overnight-infrastructure-failure-qa` -> `overnight-autonomous-orchestration`
  - `pre-publish-secret-audit` -> `pre-system-update-snapshot`
  - `workspace-ingestion` -> `gbrain-bulk-ingestion`

But this is not the missing organ TJ is asking about. It is skill-only, agent-created-only, weekly, and not a recurring-cost optimizer across crons and products. It does not own the 86 Hermes cron jobs, the 22 legacy crontab entries, or the fact that SIE and Dreamer keep proposing additions.

### Finding 7: Prior consolidations mostly did delete or archive source skills correctly, but archived skills still count in the headline 345

Concrete checks:

- `gbrain-link-recovery` claims on lines 16 to 22 that 25 retired source skills were variants around the same invariant.
- I searched for a sample of named source skills from that file and related references: `gbrain-link-recovery-may2026`, `gbrain-link-satellite-expansion`, `gbrain-link-underperformance-recovery`, `continuous-pass-3round-link-recovery`, `multi-round-link-strategy`, `idempotency-link-saturation`, `saturation-escalation`, `link-saturation-recovery-boundaries`, `domain-diversification-cron-execution`, `link-saturation-timeline-pivot`, `three-round-continuous-pass`, `saturation-recovery-three-round-pattern`.
- Those sample source skills are not lingering as active skill directories.
- Six archived skills do remain under `.archive`, and they are included in the 345 SKILL.md count but not active in the visible 339 count.

So the skill layer has had successful consolidation passes. The bigger gap is that consolidation is episodic and scoped, while addition is continuous and multi-surface.

### Finding 8: There is an untracked legacy cron layer outside the 86 Hermes jobs

`crontab -l` has 22 active lines, including:

- `task_index_sync.py` every 30 minutes.
- `ale_pattern_detect.py` daily.
- `memory-auto-indexer.py` daily.
- `archiver.py` daily.
- `memory_distill.py` daily and every 2 hours.
- `heartbeat.py` every 15 minutes.
- `email-to-brain-cron.sh` every 30 minutes.
- `ingest-sessions-to-brain.py --source jsonl` every 30 minutes.
- `ingest-sessions-to-brain.py --source archives` hourly.
- `skill-check.py` daily.
- `voice-server/scripts/watchdog.sh` every 2 minutes.

This matters because subtraction inside Hermes jobs.json alone will undercount the factory. Any later plan must include a migration decision: either import these into the Hermes scheduler with ownership metadata, or explicitly mark them out of scope with owner and reason.

## Structural root cause

The system accumulated scaffolding because incentives are one-directional:

1. Incident occurs.
2. Agent writes a skill or watcher to prevent recurrence.
3. SIE, Dreamer, skillify, and feature proposer add more follow-up work.
4. Review gates and file-write discipline make adding explicit process safer than trusting model judgment.
5. Cron removals are scary because `jobs.json` is not git-tracked and removals require soak evidence.
6. No equivalent engine asks weekly: what recurring cost can now be replaced by native model capability, a native product health surface, or one umbrella supervisor.

That is the Foxconn factory. Not one bad job. A one-way ratchet.

## What catches real failures vs alarms a worker who now shows up

Likely real failure catchers, keep or consolidate carefully:

- `mc-healthcheck`: product availability and auth path, high value because Mission Control is user-facing.
- `Cron-Heartbeat Watchdog`: scheduler liveness, high value if it checks actual execution heartbeat rather than merely jobs.json size.
- `Jobs.json Shrink Alarm`: protects against catastrophic registry loss, but should become a subcheck inside a cron supervisor.
- `GBrain Backup Restore Drill`: backup restore is materially different from health scoring.
- `MC Drift Watchdog (prod/dev split detector)`: specific class of wrong-board incident, but should be a subcheck under MC supervisor.
- `Stale Cron Path Watcher`: catches broken paths after migrations, but should be a subcheck under cron supervisor.
- `GBrain Export Watchdog`: only keep if export is consumed by a downstream user-visible surface and `GBrain Nightly Export + Push` does not already verify output.

Likely redundant or too granular as standalone crons:

- `GBrain Daily Health Check`, `GBrain Brain-Growth Audit`, `GBrain Autopilot Health Audit`, `GBrain Weekly Score Delta`, and parts of `GBrain Weekly Maintenance`, because `gbrain doctor` and `gbrain health` expose native status.
- `dispatch-coverage-daily`, `dispatch-coverage-weekly`, `routing-digest-weekly`, `routing-intel-synthesis-weekly`, `routing-intel-queue-daily`, `routing-intel-verdict-hourly`, `routing-intel-morning-digest`, because they look like a multi-cron routing analytics product that should have one owner loop.
- `Meeting Prep Auto-Watcher`, `Meeting Brief Worker`, and four `Meet EA` one-minute jobs, because six separate meeting jobs indicate a pipeline that should be event-driven or supervised as one service.
- `MC Approval Pending Mark Stale` and `MC Approval Pending Poller`, because stale marking and polling are one queue manager responsibility.

Do not delete these from this report. Use this classification to prioritize soak audits.

## Proposed plan

### Phase 0: Freeze the evidence base before any future deletion

Owner: Grant with Reid support.

Actions:

1. Write a versioned snapshot of `~/.hermes/cron/jobs.json` before any removal.
2. Write a versioned snapshot of `crontab -l`.
3. Write a skill manifest with active, archived, vendored, pinned, and hit-network classifications.
4. Add an explicit `owner`, `subsystem`, `output_contract`, `alert_contract`, and `retirement_candidate` field to every Hermes cron job.
5. For system crontab lines, add a temporary owner map so they are not invisible.

Acceptance criteria:

- Every cron has an owner and expected output.
- Every cron has a rollback record.
- Vendored `gstack-*` and `gbrain-*` skills are labeled out of scope for pruning.
- No deletion has occurred.

### Phase 1: Build the subtraction engine, not a deletion spreadsheet

Owner: Reid builds, Grant reviews.

Name: `subtraction-engine` or `gstack-subtract`.

Core behavior:

1. Read Hermes jobs.json, system crontab, skill manifests, curator logs, and recent cron outputs.
2. Compute recurring-cost signals:
   - frequency cost, for example every minute, every 5 minutes, every 15 minutes.
   - LLM-token cost, if the cron invokes an agent.
   - overlap score by subsystem and output contract.
   - native-surface score, for example `gbrain doctor` covers the same check.
   - alert-noise score from last_status and Telegram alerts.
3. Output candidates, not actions:
   - consolidate into supervisor
   - demote to subcheck
   - replace with native command
   - event-drive instead of poll
   - archive skill into umbrella
   - keep, load-bearing
4. Require a soak gate for every removal candidate.
5. Integrate with `cron-retirement-soak-gate`, not around it.

Acceptance criteria:

- Produces a markdown report and machine-readable JSON.
- Never mutates by default.
- Can explain why a candidate is safe to shadow, not safe to remove.
- Flags missing output contracts as blockers.

### Phase 2: Collapse the cron health layer into one System Supervisor

Owner: Reid implementation, Grant review, Lex approval.

Target shape:

- Keep one `System Supervisor` cron at a reasonable cadence, likely every 15 minutes for fast checks and daily for slow checks.
- Move these standalone checks into subchecks where safe:
  - `Cron Health Monitor (every 2h)`
  - `Cron-Heartbeat Watchdog (every 4h)`
  - `Jobs.json Shrink Alarm (every 30min)`
  - `Stale Cron Path Watcher (23:55)`
  - `Agent Model Drift Monitor`
  - `Verify soak_auto_flip (Day 1 shadow)`
- Preserve distinct severity routing:
  - P0: scheduler dead, jobs.json shrink, MC auth broken.
  - P1: repeated cron failures, broken output path, model config drift affecting dispatch.
  - P2: stale path, warning-level drift, slow degradation.

Soak rule:

- Run supervisor in shadow mode for 7 days.
- Compare subcheck output to old crons.
- Retire only the old crons whose outputs are fully reproduced.
- Keep old crons paused, not removed, for one additional recovery window.

### Phase 3: Collapse GBrain health supervision around native `gbrain doctor`

Owner: GBrain-aware Reid, reviewed by Grant.

Target shape:

- One GBrain health supervisor that calls `gbrain doctor --json` for full checks when appropriate and `gbrain doctor --fast --json` for fast checks.
- One backup restore drill remains separate because restore proof is not the same as health scoring.
- One ingestion or extraction pipeline remains per actual data product, but health scoring becomes native.

Candidates to consolidate or demote:

- `GBrain Daily Health Check (9am)`
- `GBrain Brain-Growth Audit (daily 11am)`
- `GBrain Autopilot Health Audit (daily 11:05am)`
- `GBrain Weekly Score Delta (Sat 7am)`
- Parts of `GBrain Weekly Maintenance (Monday 6am)`
- `GBrain Export Watchdog (daily 06:00)`, if export job verifies its own artifact

Keep separate until proven:

- `GBrain Backup Restore Drill (monthly)`
- `GBrain Native Dream (Nightly 2am)`
- `GBrain NER Relationship Extract (nightly 2:30am)`
- `GBrain Link Rebuild (Daily 2:15am)`, unless native dream fully subsumes it with output evidence

### Phase 4: Convert SIE and routing analytics from many crons into one loop with stages

Owner: Lex architecture, Reid implementation, Grant review.

Target shape:

- One `SIE Routing Intelligence Loop` with stages:
  - ingest
  - score
  - verdict
  - digest
  - coverage sample
  - weekly synthesis
- Current standalone jobs become stage definitions, not independent schedulers:
  - `routing-intel-queue-daily`
  - `routing-intel-verdict-hourly`
  - `routing-intel-morning-digest`
  - `routing-digest-weekly`
  - `routing-intel-synthesis-weekly`
  - `dispatch-coverage-daily`
  - `dispatch-coverage-weekly`
  - `sie-proposer-staleness-alarm`

Subtraction guard:

- If a stage has not produced a decision used by humans or automation in 30 days, it becomes a retirement candidate.
- If it produces only more cards about cards, it requires explicit Lex approval to remain.

### Phase 5: Turn meeting automation from polling factory into a service or event pipeline

Owner: Reid, with Cal for product workflow.

Current factory:

- `Meeting Prep Auto-Watcher` every 15 minutes.
- `Meeting Brief Worker` every 5 minutes.
- `Meet EA: Calendar Watcher` every 1 minute.
- `Meet EA: Prompt Responder` every 1 minute.
- `Meet EA: Transcript Filer` every 1 minute.
- `Meet EA: Action Extractor` every 1 minute.

Target shape:

- One Meet EA service with internal queue stages and one health heartbeat.
- Prefer calendar event triggers or a single one-minute queue poller over four one-minute crons.
- One status surface reports stage backlog and last success per stage.

Retirement criterion:

- Old crons can pause after the service reproduces all stage outputs for 7 days.

### Phase 6: Continue skill consolidation, but do it with retrieval-cost metrics

Owner: Curator for safe archive, Grant for policy.

Do not touch upstream-vendored `gstack-*` and `gbrain-*` skills.

Priority clusters inside `hit-network`:

1. GBrain operational skills. Evaluate whether `gbrain-link-rebuild`, `gbrain-link-rebuild-daily`, `gbrain-relationship-extraction-ops`, `gbrain-duplicate-detection`, `gbrain-namespace-cleanup`, and `gbrain-entity-promotion-audit` are separate class-level skills or should become sections under fewer GBrain ops umbrellas.
2. Overnight skills. Evaluate whether six overnight skills are class-level distinct or a retrieval burden.
3. Mission Control skills. Evaluate whether `mission-control-engineering`, `mission-control-filing`, `mission-control-integration`, and `mission-control-board-prod-vs-dev` need clearer routing boundaries to avoid loading the wrong giant skill.
4. Verify and audit skills. Evaluate whether `verify-before-negating-external-claims`, `verify-brain-state-before-claims`, and `verify-spec-before-claiming-done` should remain separate because their triggers are materially distinct.
5. Voice skills. Evaluate whether `voice-out-text-hygiene`, `voice-server-cloudflare-recovery`, `twilio-cloudflared-voice-server-ops`, and `tts-voice-stack` need one voice umbrella plus references.

Metric to add:

- Track skill load frequency, downstream correction rate, and prompt-token footprint per loaded skill.
- A skill is expensive if it loads often, is long, and is not cited in successful outcomes.
- A skill is dangerous if it loads often and causes over-prescription or stale bias.

### Phase 7: Move legacy system crontab into explicit governance

Owner: Grant inventory, Reid migration.

Actions:

1. Classify 22 system crontab lines as keep, import to Hermes scheduler, replace by supervisor, or retire candidate.
2. Pay special attention to overlapping memory and brain ingestion jobs:
   - `memory_distill.py` daily and every 2 hours.
   - `ingest-sessions-to-brain.py --source jsonl` every 30 minutes.
   - `ingest-sessions-to-brain.py --source archives` hourly.
   - `memory-auto-indexer.py`, `generate-memory.py`, `detect-correction.py`, `corrections-to-skill.py`, `q4-to-skill.py`.
3. Decide whether `heartbeat.py` and `voice-server/scripts/watchdog.sh` belong under System Supervisor.

Acceptance criteria:

- There is no hidden scheduler layer without owner and rollback.

## Risks

1. Single-point-of-failure risk. Collapsing five watchers into one supervisor can create a bigger outage if the supervisor fails. Mitigation: supervisor must emit its own heartbeat and have a tiny independent liveness check.
2. Quiet load-bearing risk. Some ugly cron may feed a downstream artifact nobody remembers. Mitigation: output_contract and 7-day shadow comparison before pausing.
3. Native health false-negative risk. `gbrain doctor --fast --json` skipped DB checks in my run. Mitigation: fast doctor for frequent checks, full doctor for slower checks, and explicit category coverage in supervisor output.
4. Skill injection regression risk. `prompt-compiler-operations` records a prior addition-by-subtraction attempt that broke skill injection by changing live matcher defaults from top_n 25 to 7 and relevance_floor 0.4 to 0.6. Mitigation: any skill corpus pruning must include selector regression tests and prompt-compile diff tests.
5. Archive count confusion. The headline 345 includes 6 hidden archived skills. Mitigation: future dashboards must separate active, archived, vendored, and prunable counts.
6. Approval risk. Actual removals are irreversible-ish because `jobs.json` is not git-tracked. Mitigation: no delete without TJ approval, snapshot, soak, and rollback artifact.

## Immediate next actions I recommend

1. Do not delete anything today.
2. Build the subtraction engine report-only first.
3. Start with cron consolidation, not skills, because recurring execution cost is higher than passive skill storage.
4. Make GBrain health the pilot because native `gbrain doctor` already exists and gives structured JSON.
5. Make System Supervisor the second pilot because cron watchdogs are visibly overlapping.
6. Use Curator for continued skill umbrella work, but do not pretend it solves cron and process scaffolding.

## Learnings

- The key structural smell is not high count alone. It is asymmetric governance: addition has multiple engines, subtraction has one narrow curator.
- Native health surfaces should be consumed before bespoke watchers are written. GBrain already exposes `doctor` and `health`.
- Count dashboards must distinguish active, hidden archived, vendored, and prunable assets. One number hides the actual operating surface.
- Retirement needs an engine with soak and rollback, not an agent with a broom.
- The clean target is fewer schedulers with stronger output contracts, not fewer safeguards by faith.
