# Scheduler Audit, Arm A, Hermes jobs.json

Done means every one of the 86 Hermes jobs in `/Users/TJ/.hermes/cron/jobs.json` is classified with liveness, mode, purpose, producer or guard status, script basename, consolidation cluster, and soak-gated proposals, with no deletions performed.

## Scope and method

- Scope: only `/Users/TJ/.hermes/cron/jobs.json`, 86 jobs.
- Method: parsed all job records, read inline prompts, sampled script headers and docstrings for jobs with `script`, and checked user crontab plus LaunchAgents or LaunchDaemons for exact script-basename twins.
- Constraint honored: analysis only, deleted nothing, changed no scheduler config.
- Retirement discipline: every retire or consolidation candidate below needs 7-day cron-retirement soak, coverage parity proof, and TJ approval.

## Executive summary

- Total jobs: 86.
- Enabled or scheduled: 85. Paused: 1.
- Runtime mode: 57 no_agent script jobs, 29 LLM-agent jobs.
- Classification: 55 producers, 31 guards.
- Last status: 83 ok, 1 error, 2 never-run or status-null.
- Recency: weekly/recent 36h to 8d: 25, alive 1h to 36h: 34, hot under 1h: 19, paused: 1, error: 1, stale over 8d: 4, never-run: 2.
- Jobs with script field: 61. Exact crontab script-basename twins found: 0. LaunchAgent or LaunchDaemon exact twins found: 0.
- High-confidence dead or stale findings: 1 paused legacy job, `GBrain Dream Cycle (Nightly 2am)`; 1 erroring producer, `sie-d1-daily`; 2 enabled never-run jobs, `MC Authed Convex Cron Liveness Check` and `SIE Ingest Source Health (daily 8:15am)`.
- Main root cause shape: surface fragmentation, not obvious mass dead weight. GBrain, SIE, MC, cron safety, routing intel, and Meet pipelines have many small jobs where one supervisor with subchecks would be easier to reason about.

## All jobs table

| # | Job | Schedule | Mode | State | Last status | Liveness | Deliver | Script | Class | Cluster | Purpose | Twin suspicion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Overnight Dreamer (10:30 PM) | 0 22 * * * | LLM-agent | enabled | ok | weekly/recent 1.7d | local | inline prompt | PRODUCER | Core day cycle | LLM board-first overnight planning and dispatch protocol. | none seen |
| 2 | Morning QA (5:30 AM) | 30 5 * * * | LLM-agent | enabled | ok | alive 9.4h | local | inline prompt | PRODUCER | Core day cycle | Grades overnight deliverables and writes QA report plus Dreamer feedback. | none seen |
| 3 | Morning Delivery Compile (6:30 AM) | 30 6 * * * | LLM-agent | enabled | ok | alive 9.0h | telegram:-1003914984528:1 | inline prompt | PRODUCER | Core day cycle | Compiles QA, wave timing, queue, and held notices into TJ morning delivery. | none seen |
| 4 | Lex Nightly Self-Inventory (9 PM) | 0 21 * * * | LLM-agent | enabled | ok | weekly/recent 1.8d | local | inline prompt | PRODUCER | Memory and review | source ~/hermes-workspace/Lex-Workspace/cron-env.sh Run that line before any `gbrain`, `bun`, `git`, or workspace CLI in | none seen |
| 5 | Daily Workspace Backup (11 PM) | 0 23 * * * | LLM-agent | enabled | ok | weekly/recent 1.7d | local | inline prompt | PRODUCER | Other | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 6 | ALE Session Sync (every 30min) | */30 * * * * | no_agent | enabled | ok | hot under 1h | local | ale-session-sync-wrapper.sh | PRODUCER | Memory and review | Script-driven job: ale-session-sync-wrapper.sh | conceptual crontab ALE sibling |
| 7 | Decision + Correction Extraction (11:30 PM) | 30 23 * * * | LLM-agent | enabled | ok | weekly/recent 1.6d | local | inline prompt | PRODUCER | Memory and review | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | conceptual crontab detect-correction or memory_distill sibling |
| 8 | GBrain Weekly Maintenance (Monday 6am) | 0 6 * * 1 | LLM-agent | enabled | ok | weekly/recent 2.4d | local | inline prompt | PRODUCER | GBrain | GBRAIN WEEKLY MAINTENANCE -- Full 13-dimension health sweep. BEFORE DOING ANYTHING: Read the maintain skill completely.  | none seen |
| 9 | GBrain Morning Briefing (8am) | 0 8 * * * | LLM-agent | enabled | ok | alive 7.4h | telegram:-1003914984528:1 | inline prompt | PRODUCER | GBrain | GBRAIN MORNING BRIEFING -- Daily intelligence briefing for TJ. BEFORE DOING ANYTHING: Read the briefing skill completely | none seen |
| 10 | GBrain Workspace Ingestion | 0 1,7,13,19 * * * | LLM-agent | enabled | ok | alive 2.4h | telegram:-1003914984528:256 | inline prompt | PRODUCER | GBrain | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 11 | GBrain Daily Health Check (9am) | 0 9 * * * | LLM-agent | enabled | ok | alive 5.0h | local | inline prompt | GUARD | GBrain | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 12 | Lex Sunday Review (Self-Assessment + Memory Maintenance, 10 AM) | 0 10 * * 0 | LLM-agent | enabled | ok | weekly/recent 3.2d | telegram:-1003914984528:1 | inline prompt | PRODUCER | Memory and review | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 13 | Lex Monthly Review (1st of month, 10 AM) | 0 10 1 * * | LLM-agent | enabled | ok | weekly/recent 2.2d | telegram:-1003914984528:1 | inline prompt | PRODUCER | Memory and review | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 14 | GBrain Auto-Update Watcher (Daily 4am) | 0 4 * * * | LLM-agent | enabled | ok | alive 11.5h | local | inline prompt | GUARD | GBrain | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 15 | GBrain Weekly Score Delta (Sat 7am) | 0 7 * * 6 | LLM-agent | enabled | ok | weekly/recent 4.4d | local | inline prompt | GUARD | GBrain | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 16 | GBrain Backup Restore Drill (monthly) | 0 4 1 * * | LLM-agent | enabled | ok | weekly/recent 2.5d | local | gbrain-backup-drill.py | GUARD | GBrain | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | duplicate copy or shim |
| 17 | GBrain Dream Cycle (Nightly 2am) | 0 2 * * * | LLM-agent | paused | ok | paused, last 3.6d ago | local | inline prompt | PRODUCER | GBrain | Paused legacy LLM GBrain dream maintenance, superseded by native dream. | none seen |
| 18 | GBrain Link Rebuild (Daily 2:15am) | 15 2 * * * | LLM-agent | enabled | ok | alive 12.7h | local | inline prompt | PRODUCER | GBrain | GBRAIN DAILY LINK REBUILD -- catches sync drift and rebuilds mention edges. This is infrastructure maintenance. No deliv | none seen |
| 19 | GBrain Brain-Growth Audit (daily 11am) | 0 11 * * * | no_agent | enabled | ok | alive 4.5h | telegram:-1003914984528:256 | gbrain-brain-growth-audit.py | GUARD | GBrain | Brain-growth audit. Silent on PASS, loud on FAIL. Plan: ~/hermes-workspace/Lex-Workspace/tasks/plans/2026-05-18-soak-aud | none seen |
| 20 | Cron Health Monitor (every 2h) | 0 */2 * * * | LLM-agent | enabled | ok | alive 1.5h | telegram:-1003914984528:256 | inline prompt | GUARD | Cron safety | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 21 | Memory Health Check (Daily 3am) | 0 3 * * * | LLM-agent | enabled | ok | alive 12.5h | telegram:-1003914984528:256 | inline prompt | GUARD | Memory and review | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | conceptual crontab memory_health sibling |
| 22 | mc-nightly-backup (2am) | 0 2 * * * | LLM-agent | enabled | ok | alive 12.7h | local | inline prompt | PRODUCER | Mission Control | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 23 | Jobs.json Shrink Alarm (every 30min) | */30 * * * * | LLM-agent | enabled | ok | hot under 1h | telegram:-1003914984528:256 | inline prompt | GUARD | Cron safety | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 24 | Agent Model Drift Monitor | 0 7 * * * | LLM-agent | enabled | ok | alive 8.5h | telegram:-1003914984528:256 | inline prompt | GUARD | Other | Run that line before any `gbrain`, `bun`, `git`, or workspace CLI invocation. The `.local/bin/gbrain` shim is the actual | none seen |
| 25 | calendar-to-brain | 0 10 * * 1,3,5 | no_agent | enabled | ok | alive 4.9h | local | calendar-to-brain-cron.sh | PRODUCER | GBrain | Script-driven job: calendar-to-brain-cron.sh | none seen |
| 26 | Lex-Workspace Collector (every 30min) | */30 * * * * | no_agent | enabled | ok | hot under 1h | local | lex-workspace-collector-cron.sh | PRODUCER | GBrain | Script-driven job: lex-workspace-collector-cron.sh | none seen |
| 27 | GBrain Embed Safety-Net (every 15 min) | */15 * * * * | LLM-agent | enabled | ok | hot under 1h | local | inline prompt | PRODUCER | GBrain | GBRAIN EMBED SAFETY-NET -- catches any unembedded chunks (collector failures, prior --no-embed runs). Architectural cont | none seen |
| 28 | lex-workspace-synthesis-mirror | hourly | LLM-agent | enabled | ok | hot under 1h | local | lex-workspace-synthesis-mirror.sh | PRODUCER | Other | Script-driven job: lex-workspace-synthesis-mirror.sh | none seen |
| 29 | GBrain Central-Node Audit (weekly, Mon 09:00 ET) | 0 9 * * 1 | LLM-agent | enabled | ok | weekly/recent 2.3d | local | gbrain-central-node-audit.py | GUARD | GBrain | GBrain central-node audit. Script output (JSON) is appended above. Parse it. If total_flagged > 0 and any flagged entry  | none seen |
| 30 | youtube-channel-poll | 0 */4 * * * | no_agent | enabled | ok | alive 3.5h | local | youtube-channel-poll.sh | PRODUCER | GBrain | Script-driven job: youtube-channel-poll.sh | none seen |
| 31 | youtube-channel-enrich | */15 * * * * | no_agent | enabled | ok | hot under 1h | local | youtube-channel-enrich.sh | PRODUCER | GBrain | Script-driven job: youtube-channel-enrich.sh | none seen |
| 32 | web-to-brain-enrich | */15 * * * * | no_agent | enabled | ok | hot under 1h | local | web-to-brain-enrich.sh | PRODUCER | GBrain | web-to-brain enrichment-queue drainer. Watchdog mode. | none seen |
| 33 | GBrain Nightly Export + Push | 0 4 * * * | no_agent | enabled | ok | alive 11.5h | local | gbrain-nightly-export.sh | PRODUCER | GBrain | Nightly export of GBrain to filesystem mirror + git commit + push to LexClaw/gbrain-pages. See plan 2026-05-15-gbrain-ba | duplicate copy or shim |
| 34 | Daily Curated Writer - Yesterday (00:10) | 10 0 * * * | no_agent | enabled | ok | weekly/recent 1.6d | local | daily-curated-yesterday.sh | PRODUCER | GBrain | Script-driven job: daily-curated-yesterday.sh | none seen |
| 35 | Daily Curated Writer - Today Stub (00:15) | 15 0 * * * | no_agent | enabled | ok | weekly/recent 1.6d | local | daily-curated-today-stub.sh | PRODUCER | GBrain | Script-driven job: daily-curated-today-stub.sh | none seen |
| 36 | Daily Curated Writer - Today Refresh (22:30) | 30 22 * * * | no_agent | enabled | ok | weekly/recent 1.7d | local | daily-curated-today-refresh.sh | PRODUCER | GBrain | Script-driven job: daily-curated-today-refresh.sh | none seen |
| 37 | QUICKREF Refresh (Sunday 23:00) | 0 23 * * 0 | no_agent | enabled | ok | weekly/recent 2.7d | local | quickref-refresh-weekly.sh | PRODUCER | GBrain | Script-driven job: quickref-refresh-weekly.sh | none seen |
| 38 | GBrain Export Watchdog (daily 06:00) | 0 6 * * * | no_agent | enabled | ok | alive 9.5h | telegram:-1003914984528:256 | gbrain-nightly-export-watchdog.sh | GUARD | GBrain | Watchdog for GBrain nightly export. Silent on healthy. Alerts on failed/stuck/stale. Plan: ~/hermes-workspace/Lex-Worksp | none seen |
| 39 | GBrain Autopilot Health Audit (daily 11:05am) | 5 11 * * * | no_agent | enabled | ok | alive 4.4h | telegram:-1003914984528:256 | gbrain-autopilot-health-audit.py | GUARD | GBrain | Autopilot process-health audit (cycles + errors). Silent on PASS, loud on FAIL. Plan: ~/hermes-workspace/Lex-Workspace/t | none seen |
| 40 | sync_task_index_from_convex | 0 7 * * * | no_agent | enabled | ok | alive 8.5h | local | sync-task-index-from-convex.sh | PRODUCER | Mission Control | Daily 7am ET: regenerate TASK_INDEX.md from Convex MC board (card kn7835p0sr). | conceptual crontab task_index_sync sibling |
| 41 | mc-healthcheck | */5 * * * * | no_agent | enabled | ok | hot under 1h | telegram:-1003914984528:256 | mc-healthcheck.sh | GUARD | Mission Control | Mission Control healthcheck watchdog. Probes /api/internal/healthz every 5 min; alerts to LexTech topic 256 on 2 consecu | none seen |
| 42 | MC Overnight Reports Collector | 0 7 * * * | no_agent | enabled | ok | alive 8.5h | origin | mc-overnight-report-collector.sh | PRODUCER | Mission Control | Script-driven job: mc-overnight-report-collector.sh | none seen |
| 43 | MC People Graph Export | 0 6 * * * | no_agent | enabled | ok | alive 9.5h | origin | mc-export-people-graph.sh | PRODUCER | Mission Control | Script-driven job: mc-export-people-graph.sh | none seen |
| 44 | sie-d1-daily | 30 23 * * * | no_agent | enabled | error | error, last 1.6d ago | telegram:484310440 | sie-d1-daily-wrapper.sh | PRODUCER | SIE | Daily SIE profile ingest producer. | none seen |
| 45 | sie-d2-weekly | 0 23 * * 0 | no_agent | enabled | ok | weekly/recent 2.7d | telegram:484310440 | sie-d2-weekly-wrapper.sh | PRODUCER | SIE | Script-driven job: sie-d2-weekly-wrapper.sh | none seen |
| 46 | sie-f-mirror | 30 23 * * 0 | no_agent | enabled | ok | stale 8.1d | telegram:484310440 | sie-f-mirror-wrapper.sh | PRODUCER | SIE | Script-driven job: sie-f-mirror-wrapper.sh | none seen |
| 47 | sie-f-audit | 0 8 * * 1 | LLM-agent | enabled | ok | weekly/recent 2.3d | telegram:484310440 | inline prompt | GUARD | SIE | Read and execute the instructions in /Users/TJ/hermes-workspace/Lex-Workspace/cron-prompts/sie-f-audit.md exactly as wri | none seen |
| 48 | MC Drift Watchdog (prod/dev split detector) | 0 * * * * | no_agent | enabled | ok | hot under 1h | origin | mc-drift-watchdog.sh | GUARD | Mission Control | Script-driven job: mc-drift-watchdog.sh | none seen |
| 49 | sie-scorecard-weekly | 45 23 * * 0 | no_agent | enabled | ok | stale 8.1d | telegram:484310440 | sie-scorecard-weekly-wrapper.sh | GUARD | SIE | Script-driven job: sie-scorecard-weekly-wrapper.sh | none seen |
| 50 | sie-improvement-proposer-daily | 0 6 * * * | no_agent | enabled | ok | alive 9.5h | origin | sie-proposer-daily.sh | PRODUCER | SIE | Script-driven job: sie-proposer-daily.sh | none seen |
| 51 | SIE Self-Inventory v2 (nightly 23:00) | 0 23 * * * | no_agent | enabled | ok | weekly/recent 1.7d | local | sie-self-inventory-v2.sh | PRODUCER | SIE | Script-driven job: sie-self-inventory-v2.sh | none seen |
| 52 | quiet-period-detection-6h | 0 */6 * * * | no_agent | enabled | ok | alive 3.5h | local | quiet-period-detection.sh | PRODUCER | SIE | Script-driven job: quiet-period-detection.sh | none seen |
| 53 | sie-learnings-compaction-weekly | 0 2 * * 0 | no_agent | enabled | ok | weekly/recent 3.6d | local | sie-learnings-compaction.sh | PRODUCER | SIE | Script-driven job: sie-learnings-compaction.sh | none seen |
| 54 | sie-pin-audit-weekly | 35 23 * * 0 | no_agent | enabled | ok | stale 9.7d | local | sie-pin-audit.sh | GUARD | SIE | Script-driven job: sie-pin-audit.sh | none seen |
| 55 | sie-skillify-weekly | 0 10 * * 2 | no_agent | enabled | ok | alive 29.5h | origin | sie-skillify.sh | PRODUCER | SIE | Script-driven job: sie-skillify.sh | none seen |
| 56 | dispatch-coverage-daily | 30 6 * * * | no_agent | enabled | ok | alive 9.0h | local | dispatch-coverage-sampler.sh | GUARD | SIE | Script-driven job: dispatch-coverage-sampler.sh | none seen |
| 57 | dispatch-coverage-weekly | 30 23 * * 0 | no_agent | enabled | ok | stale 9.7d | local | dispatch-coverage-weekly.sh | GUARD | SIE | Script-driven job: dispatch-coverage-weekly.sh | none seen |
| 58 | routing-digest-weekly | 0 21 * * 0 | no_agent | enabled | ok | weekly/recent 2.8d | telegram | routing-digest-weekly.sh | GUARD | Routing intel | Script-driven job: routing-digest-weekly.sh | none seen |
| 59 | routing-intel-synthesis-weekly | 30 21 * * 0 | no_agent | enabled | ok | weekly/recent 2.8d | origin | routing-intel-synthesis-weekly.sh | PRODUCER | Routing intel | Script-driven job: routing-intel-synthesis-weekly.sh | none seen |
| 60 | routing-intel-queue-daily | 0 6 * * * | no_agent | enabled | ok | alive 9.5h | origin | routing-intel-queue-daily.sh | PRODUCER | Routing intel | Script-driven job: routing-intel-queue-daily.sh | duplicate copy or shim |
| 61 | iMessage Adapter (30min poll) | */30 * * * * | no_agent | enabled | ok | hot under 1h | local | imessage-adapter-cron.sh | PRODUCER | Personal intake | Script-driven job: imessage-adapter-cron.sh | none seen |
| 62 | routing-intel-verdict-hourly | 0 * * * * | no_agent | enabled | ok | hot under 1h | telegram:-1003914984528:256 | routing-intel-verdict-hourly.sh | PRODUCER | Routing intel | Script-driven job: routing-intel-verdict-hourly.sh | none seen |
| 63 | Cron-Heartbeat Watchdog (every 4h) | 0 */4 * * * | LLM-agent | enabled | ok | alive 3.5h | telegram:-1003914984528:256 | cron-heartbeat-watchdog.py | GUARD | Cron safety | The script `~/.hermes/scripts/cron-heartbeat-watchdog.py` ran and is silent when everything is healthy. You only see thi | none seen |
| 64 | routing-intel-morning-digest | 30 6 * * * | no_agent | enabled | ok | alive 9.0h | local | routing-intel-morning-digest.sh | PRODUCER | Routing intel | Script-driven job: routing-intel-morning-digest.sh | none seen |
| 65 | sie-promote-token-cleanup | 0 * * * * | no_agent | enabled | ok | hot under 1h | local | sie-promote-token-cleanup.sh | GUARD | SIE | Script-driven job: sie-promote-token-cleanup.sh | none seen |
| 66 | Meeting Prep Auto-Watcher | */15 * * * * | no_agent | enabled | ok | hot under 1h | telegram:-1003914984528:1 | meeting-prep-watcher.py | PRODUCER | Meeting prep | Meeting prep watcher; script-driven (no_agent=true), prompt ignored at runtime. After meeting-brief-mark-done.py validat | none seen |
| 67 | Meeting Brief Worker (every 5min) | */5 * * * * | no_agent | enabled | ok | hot under 1h | telegram:-1003914984528:256 | meeting-brief-worker.py | PRODUCER | Meeting prep | Meeting brief worker; script-driven, prompt ignored. Picks briefed-pending entries from ~/.hermes/state/meeting-prep-wat | none seen |
| 68 | MC Feature Suggester (nightly proposer) | 50 23 * * * | LLM-agent | enabled | ok | weekly/recent 1.6d | local | inline prompt | PRODUCER | Mission Control | # MC Feature Suggester (nightly proposer) ## Identity You are **Cal**, the research/synthesis agent for Hit Network. Ton | none seen |
| 69 | Synthesis-Page Staleness Surface (discipline-gap card filer) | 30 21 * * * | no_agent | enabled | ok | weekly/recent 1.8d | telegram:-1003914984528:256 | discipline-gap-card-filer-wrapper.sh | GUARD | SIE | Run discipline-gap-card-filer.py and report the exit code. | none seen |
| 70 | Stale Cron Path Watcher (23:55) | 55 23 * * * | no_agent | enabled | ok | weekly/recent 1.6d | local | stale-cron-path-watcher.py | GUARD | Cron safety | Script-driven job: stale-cron-path-watcher.py | none seen |
| 71 | Overnight Executor (11pm-6am, board-drainer) | 0 23 * * * | no_agent | enabled | ok | weekly/recent 1.6d | telegram:-1003914984528:256 | overnight-executor.sh | PRODUCER | Core day cycle | Script-driven job: overnight-executor.sh | none seen |
| 72 | MC Stuck in_progress Audit | 0 6 * * * | no_agent | enabled | ok | alive 9.5h | origin | stuck-in-progress-audit.sh | GUARD | Mission Control | Script-driven job: stuck-in-progress-audit.sh | none seen |
| 73 | repos-tracking-weekly | 0 9 * * 0 | LLM-agent | enabled | ok | weekly/recent 3.3d | telegram:-1003914984528:1 | inline prompt | PRODUCER | Personal intake | Weekly tracking pass - Hit Network external-tool watchlist. Reads canonical registers (do NOT bypass): - lex-workspace/r | none seen |
| 74 | MC Approval Pending Mark Stale | 0 13 * * * | no_agent | enabled | ok | alive 2.5h | origin | approval-pending-mark-stale.py | PRODUCER | Mission Control | Script-driven job: approval-pending-mark-stale.py | none seen |
| 75 | MC Approval Pending Poller | */30 * * * * | no_agent | enabled | ok | hot under 1h | telegram:-1003914984528:256 | approval-pending-poller.py | GUARD | Mission Control | Script-driven job: approval-pending-poller.py | none seen |
| 76 | Verify soak_auto_flip (Day 1 shadow) | 0 6 * * * | no_agent | enabled | ok | alive 9.5h | local | verify-soak-auto-flip.sh | GUARD | Mission Control | Script-driven job: verify-soak-auto-flip.sh | none seen |
| 77 | Missing-Link Coverage Harvester (07:30 ET) | 30 7 * * * | no_agent | enabled | ok | alive 7.5h | telegram:-1003914984528:256 | auto-enrich-coverage-harvester.sh | GUARD | GBrain | Script-driven job: auto-enrich-coverage-harvester.sh | none seen |
| 78 | Meet EA: Calendar Watcher (every 1 min) | every 1m | no_agent | enabled | ok | hot under 1h | local | meet-calendar-watcher.py | PRODUCER | Meet EA | Script-driven job: meet-calendar-watcher.py | duplicate copy or shim |
| 79 | Meet EA: Prompt Responder (every 1 min) | every 1m | no_agent | enabled | ok | hot under 1h | local | meet-prompt-responder.py | PRODUCER | Meet EA | Script-driven job: meet-prompt-responder.py | duplicate copy or shim |
| 80 | Meet EA: Transcript Filer (every 1 min) | every 1m | no_agent | enabled | ok | hot under 1h | local | meet-transcript-filer.py | PRODUCER | Meet EA | Script-driven job: meet-transcript-filer.py | duplicate copy or shim |
| 81 | Meet EA: Action Extractor (every 1 min) | every 1m | no_agent | enabled | ok | hot under 1h | local | meet-action-extractor.py | PRODUCER | Meet EA | Script-driven job: meet-action-extractor.py | duplicate copy or shim |
| 82 | sie-proposer-staleness-alarm | 30 6 * * * | no_agent | enabled | ok | alive 9.0h | local | sie-proposer-staleness-alarm.sh | GUARD | SIE | Script-driven job: sie-proposer-staleness-alarm.sh | none seen |
| 83 | GBrain Native Dream (Nightly 2am) | 0 2 * * * | no_agent | enabled | ok | alive 12.6h | origin | gbrain-dream-native-wrapper.sh | PRODUCER | GBrain | Deterministic native gbrain dream cycle replacing paused LLM dream. | none seen |
| 84 | GBrain NER Relationship Extract (nightly 2:30am) | 30 2 * * * | no_agent | enabled | ok | alive 12.7h | origin | gbrain-ner-nightly.sh | PRODUCER | GBrain | Script-driven job: gbrain-ner-nightly.sh | none seen |
| 85 | MC Authed Convex Cron Liveness Check | 0 10 * * 1 | no_agent | enabled | none | never-run | origin | mc-authed-cron-liveness-check.sh | GUARD | Cron safety | Weekly positive liveness audit for Hermes scripts touching authed Convex. | none seen |
| 86 | SIE Ingest Source Health (daily 8:15am) | 15 8 * * * | no_agent | enabled | none | never-run | telegram:-1003914984528:256 | sie-ingest-source-health.py | GUARD | SIE | Checks SIE ingest source and output freshness. | duplicate copy or shim |

## Consolidation proposals, soak-gated

### GBrain supervisor

- Candidate: 8 to 1.
- Jobs: `GBrain Daily Health Check (9am)`, `GBrain Brain-Growth Audit (daily 11am)`, `GBrain Autopilot Health Audit (daily 11:05am)`, `GBrain Central-Node Audit (weekly, Mon 09:00 ET)`, `GBrain Weekly Score Delta (Sat 7am)`, `GBrain Auto-Update Watcher (Daily 4am)`, `GBrain Export Watchdog (daily 06:00)`, `Missing-Link Coverage Harvester (07:30 ET)`.
- Rationale: Consolidate guard reporting, keep producers independent.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

### Cron scheduler safety supervisor

- Candidate: 4 to 1.
- Jobs: `Cron Health Monitor (every 2h)`, `Jobs.json Shrink Alarm (every 30min)`, `Cron-Heartbeat Watchdog (every 4h)`, `Stale Cron Path Watcher (23:55)`.
- Rationale: Replace incident-scaffold alarms with one positive-liveness supervisor after shadow parity.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

### SIE supervisor

- Candidate: 17 to 1.
- Jobs: `sie-d1-daily`, `sie-d2-weekly`, `sie-f-mirror`, `sie-f-audit`, `sie-scorecard-weekly`, `sie-improvement-proposer-daily`, `SIE Self-Inventory v2 (nightly 23:00)`, `quiet-period-detection-6h`, `sie-learnings-compaction-weekly`, `sie-pin-audit-weekly`, `sie-skillify-weekly`, `dispatch-coverage-daily`, `dispatch-coverage-weekly`, `sie-proposer-staleness-alarm`, `SIE Ingest Source Health (daily 8:15am)`, `Synthesis-Page Staleness Surface (discipline-gap card filer)`, `sie-promote-token-cleanup`.
- Rationale: Highest complexity cluster. Start with health, staleness, scorecard, and coverage. Do not merge red D1 until fixed.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

### Mission Control supervisor

- Candidate: 8 to 1.
- Jobs: `mc-healthcheck`, `MC Drift Watchdog (prod/dev split detector)`, `MC Stuck in_progress Audit`, `MC Approval Pending Mark Stale`, `MC Approval Pending Poller`, `Verify soak_auto_flip (Day 1 shadow)`, `MC Authed Convex Cron Liveness Check`, `sync_task_index_from_convex`.
- Rationale: Unify MC health and authed Convex liveness while keeping backups and exports independent.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

### Routing intel supervisor

- Candidate: 5 to 1.
- Jobs: `routing-digest-weekly`, `routing-intel-synthesis-weekly`, `routing-intel-queue-daily`, `routing-intel-verdict-hourly`, `routing-intel-morning-digest`.
- Rationale: Natural queue to verdict to digest pipeline.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

### Meet EA pipeline supervisor

- Candidate: 4 to 1.
- Jobs: `Meet EA: Calendar Watcher (every 1 min)`, `Meet EA: Prompt Responder (every 1 min)`, `Meet EA: Transcript Filer (every 1 min)`, `Meet EA: Action Extractor (every 1 min)`.
- Rationale: Best pure consolidation candidate: same cadence, workdir, family, and shim pattern.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

### Meeting prep supervisor

- Candidate: 2 to 1.
- Jobs: `Meeting Prep Auto-Watcher`, `Meeting Brief Worker (every 5min)`.
- Rationale: Maybe keep split because watcher and worker have different cadences and failure blast radii.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

### Daily curated writer supervisor

- Candidate: 4 to 1.
- Jobs: `Daily Curated Writer - Yesterday (00:10)`, `Daily Curated Writer - Today Stub (00:15)`, `Daily Curated Writer - Today Refresh (22:30)`, `QUICKREF Refresh (Sunday 23:00)`.
- Rationale: Low-risk family consolidation with time-gated subcommands.
- Gate: 7-day soak with current jobs still running, parity report per subcheck, no loss of alerts, TJ approval before disabling old entries.

## Dead, stale, and retire candidates

### Strong retire candidates after soak

- `GBrain Dream Cycle (Nightly 2am)`: paused, last ok 2026-05-31, legacy LLM-prompt dream cycle. `GBrain Native Dream (Nightly 2am)` says it replaces the retired custom LLM dream cron `a89b3f576c5f`. Archive only after native dream parity is proven for 7 days.
- `Jobs.json Shrink Alarm (every 30min)`: real incident scar, but narrow and high-frequency. Merge into Cron scheduler safety supervisor after shadow parity. Not a blind deletion candidate.
- `Verify soak_auto_flip (Day 1 shadow)`: explicitly Day 1 shadow verifier. Retire only if MC authed liveness or a supervisor proves equivalent coverage.
- `Agent Model Drift Monitor`: historical drift detector that can become an MC or agent-config supervisor subcheck instead of standalone LLM-agent guard.

### Needs root-cause before any retire decision

- `sie-d1-daily`: enabled and last_status=error on 2026-06-02. This is a producer, not dead weight. Fix before consolidation.
- `MC Authed Convex Cron Liveness Check`: enabled, never-run, weekly Monday 10:00. May simply not have reached its first tick. Judge after next scheduled Monday.
- `SIE Ingest Source Health (daily 8:15am)`: enabled, never-run. Daily cadence means it should run within 24h of creation. If still null after the next 08:15 ET, investigate registration or script path.
- `sie-f-mirror`, `sie-scorecard-weekly`, `dispatch-coverage-weekly`, and `sie-pin-audit-weekly`: recent timestamps do not match expected weekly cadence cleanly. Verify scheduler output before action.

## Guard-vs-producer analysis

- Producers create durable value: files, GBrain pages or edges, MC cards, backups, reports, queue work, briefs, digests, or ingestion. Count: 55.
- Guards detect failure classes: stale data, missing paths, drift, liveness, source health, coverage, model drift, queue staleness, health endpoints, and scheduler shrink. Count: 31.
- Guards catching real historical failure classes: `Jobs.json Shrink Alarm`, `Stale Cron Path Watcher`, `Cron-Heartbeat Watchdog`, `GBrain Export Watchdog`, `GBrain Autopilot Health Audit`, `GBrain Brain-Growth Audit`, `mc-healthcheck`, `MC Drift Watchdog`, `SIE Ingest Source Health`, `dispatch-coverage-daily`, `dispatch-coverage-weekly`. Keep coverage, but not necessarily as standalone jobs.
- Guards that look like alarms for workers that usually show up on time or one-off shadows: `Verify soak_auto_flip (Day 1 shadow)`, `Agent Model Drift Monitor`, and parts of `Jobs.json Shrink Alarm` after a scheduler supervisor exists.
- Defense-in-depth that should survive until parity is proven: cron scheduler safety and SIE source health. The recent blind cut that broke dispatches makes positive assertion mandatory before removal.

## Script cross-reference and twin suspicion

- Script field jobs: 61.
- Exact crontab script-basename twins found: 0.
- LaunchAgent or LaunchDaemon exact script-basename twins found: 0.
- Duplicate same-basename copies or shims: `gbrain-backup-drill.py`, `gbrain-nightly-export.sh`, `routing-intel-queue-daily.sh`, `meet-calendar-watcher.py`, `meet-prompt-responder.py`, `meet-transcript-filer.py`, `meet-action-extractor.py`, `sie-ingest-source-health.py`. These are mostly shims or copied canonical scripts, not proven double-scheduling.
- Conceptual twins in crontab, not exact basename: memory and ALE jobs overlap with `Memory Health Check`, `Decision + Correction Extraction`, and `ALE Session Sync`; `task_index_sync.py` overlaps conceptually with `sync_task_index_from_convex`; session and email ingestion overlap with GBrain ingestion families. Sibling arms should verify whether these are intentional split surfaces or legacy duplicates.

## Honest risks

- Consolidating guards creates a single point of failure. Mitigate with supervisor self-heartbeat, per-subcheck state files, independent failure path, and 7-day side-by-side soak.
- Consolidating producers increases blast radius. Keep high-value producers independent unless they are same cadence, same workdir, same state, and already stage-like, as with Meet EA.
- Scheduler guards are tempting cuts, but they exist because scheduler deletion broke dispatches recently. Replace with positive liveness assertions, do not just delete.
- Never-run jobs may be newly created. Do not mark dead until expected cadence has passed.

## Recommended order of operations

1. Fix `sie-d1-daily` and inspect stale weekly SIE jobs.
2. Wait for or manually verify next run of `MC Authed Convex Cron Liveness Check` and `SIE Ingest Source Health (daily 8:15am)`.
3. Build Cron scheduler safety supervisor in shadow mode, leave current four guards unchanged for 7 days.
4. Build GBrain health supervisor in shadow mode, keep producers independent.
5. Merge pure Meet EA four-job pipeline if 7-day latency and output parity pass.
6. Retire old entries only with TJ approval, one cluster at a time.

## Learnings

- The scheduler is mostly alive: 82 ok, 1 current error, 2 never-run, 1 paused.
- The elegance opportunity is supervisor consolidation, not mass deletion.
- Highest-yield simplification clusters: GBrain, SIE, MC, cron safety, routing intel, Meet EA.
- Exact crontab or launchd double-scheduling was not found for script basenames, but conceptual overlap with legacy crontab jobs remains for sibling-arm verification.
- Guard quality varies. Some guards are incident scar tissue that still catches real failure modes. Others are temporary shadows that should expire through a soak gate.
