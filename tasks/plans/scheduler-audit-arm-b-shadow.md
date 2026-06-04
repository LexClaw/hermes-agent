# Scheduler Fleet Audit, Arm B: The SHADOW Layer (crontab + launchd)

Author: Grant (Sr. Systems Engineer)
Date: 2026-06-03
Surface: macOS user crontab (22 lines) + ~/Library/LaunchAgents (35 active plists)
Methodology: gstack-investigate. Reality verified via log-file mtimes and live PIDs, NOT schedules.
Constraint: ANALYSIS ONLY. Nothing was unloaded, deleted, or modified. Read-only audit.

## FINAL OUTCOME (one line)
Characterize the highest-risk, never-before-audited scheduler surface: resolve the 5 cross-surface double-schedules with log-mtime evidence, flag dead scripts, and map the memory + voice clusters, so Lex can plan a safe consolidation without repeating the blind-subtraction breakage from 4 days ago.

## VERDICT: REJECTED (surface is unsafe as-is)

This surface carries 3 active correctness bugs and 2 dead schedules logging errors on a timer. It is not Garry-Tan elegant; it is two uncoordinated schedulers firing overlapping jobs. Required changes are separated from suggested changes at the bottom. Confidence: I stake my reputation on every double-fire finding below, each is backed by a log mtime or a run-marker count, not by reading the schedule.

---

## 1. The 5 Double-Schedules, Resolved With Evidence

The dangerous discovery confirmed: 5 scripts are scheduled in BOTH crontab and launchd. The question was whether both fire (double-execution bug) or one silently superseded the other. Answer per script below. Three genuinely double-fire. Two are dead on both surfaces.

### 1.1 memory_distill.py, DOUBLE-FIRES, DIFFERENT SCRIPTS (worst kind)
- crontab: `50 23` AND `0 */2` running `/Users/TJ/hermes-workspace/Lex-Workspace/scripts/memory_distill.py` -> `~/.hermes/logs/distill-memory.log`
- launchd `ai.hitnetwork.memory-distill`: 23:25 running `/Users/TJ/.hermes/workspace/scripts/memory_distill.py` -> `~/.hermes/logs/memory-distill.log`
- EVIDENCE: distill-memory.log (cron) shows runs at 00:00, 02:00, 04:00 ... 22:00 (the `0 */2`) PLUS a 23:50 run (the `50 23`). memory-distill.log (launchd) shows "Memory distillation starting at 23:25" repeated nightly.
- VERDICT: Both surfaces fire, AND they invoke TWO DIFFERENT copies of memory_distill.py at two different paths writing two different logs. This is worse than a duplicate; it is a fork. 13 cron runs/day + 1 launchd run/day = 14 distills/day against MEMORY.md. The 13 `0 */2` + `50 23` cron runs are almost certainly accidental over-scheduling (distill is a nightly job, not a 2-hourly one). Both write MEMORY.md, so there is a real write-race window.
- KEEP: the launchd job (single nightly fire, clean log, canonical `.hermes/workspace/scripts` path). RETIRE: all 3 cron distill lines after confirming the two script copies are byte-identical or reconciling them.

### 1.2 task_index_sync.py, DOUBLE-FIRES, SAME SCRIPT, AND BROKEN
- crontab: `*/30` -> `/Users/TJ/.hermes/workspace/scripts/task_index_sync.py` -> `task-index-sync-cron.log`
- launchd `ai.hitnetwork.task-index-sync`: StartInterval 1800 (30 min), RunAtLoad true, SAME script, SAME log file
- EVIDENCE: SAME script, SAME 30-min cadence, SAME log. The shared log has 4,108 "Fetching cards from Convex prod" run-markers and is 2.27 MB. Cron (48/day) + launchd (48/day) = ~96 fires/day. Worse, EVERY run ends in `FileNotFoundError: [Errno 2] No such file or directory: 'npx'` and `InvalidDeploymentName: Couldn't parse deployment name " mission-control"` (note the leading space in the deployment name).
- VERDICT: Double-fire AND broken. The script produces zero useful output; it just doubles the error rate and balloons a 2 MB log. Two bugs: (a) double-schedule, (b) `npx` not on the launchd/cron PATH and a malformed `CONVEX_DEPLOYMENT` value (leading space, and it must use the deployment name not "mission-control"; see Grant pitfall: Convex CLI has no `--prod`, use `CONVEX_DEPLOYMENT` env var).
- KEEP: launchd (RunAtLoad gives a run on boot, StartInterval is self-healing). RETIRE: cron `*/30` line. THEN fix the npx PATH + deployment-name bug separately. Do not migrate a broken job.

### 1.3 memory-auto-indexer.py, DOUBLE-FIRES, SAME SCRIPT, SAME MINUTE, DIFFERENT LOGS (race confirmed)
- crontab: `15 23` -> `/Users/TJ/.hermes/workspace/scripts/memory-auto-indexer.py` -> `~/.hermes/workspace/logs/memory-indexer.log`
- launchd `ai.hitnetwork.memory-auto-indexer`: 23:15, SAME script -> `~/.hermes/workspace/tasks/memory-auto-indexer-cron.log`
- EVIDENCE: Both logs last-modified 2026-06-02, cron log at 23:15:00 and launchd log at 23:15:01, ONE SECOND APART. Cron log shows "Files skipped: 3854", launchd log shows "Files skipped: 3857". Both scanned the same corpus concurrently.
- VERDICT: This is the textbook double-execution race. Same script, same scheduled minute, two schedulers, both fired within 1 second of each other last night, both walked the same file tree and upserted into the same index. "Entities upserted: 0" on both, so no data corruption observed yet, but two concurrent indexers against one store is a latent corruption/lock bug. Also both log `[WikiIndex] SKIP: wiki-indexer.py not found` (a dead dependency, see section 3).
- KEEP: launchd. RETIRE: cron `15 23` line.

### 1.4 generate-memory.py, DOUBLE-FIRES, SAME SCRIPT, SAME LOG, NOW HEALTHY
- crontab: `45 23` -> `/Users/TJ/.hermes/workspace/scripts/generate-memory.py` -> `~/.hermes/logs/generate-memory.log`
- launchd `ai.hitnetwork.generate-memory`: 23:03, SAME script, SAME log
- EVIDENCE: 80 "Generated:" success markers in the shared log; latest runs report "Entities: 39312, Relationships: 1656". Two scheduled times (23:03 launchd, 23:45 cron) = 2 generations/night. Log lines 1-2 are old `can't open file ... generate-memory.py` errors; first success is line 18. The script was MISSING and has since been RESTORED; it is healthy now.
- VERDICT: Double-fire, both succeed, same output file (`MEMORY.md.generated`) regenerated twice nightly 42 min apart. Wasteful (full 39K-entity regen twice) but not corrupting since it is idempotent regeneration. The earlier missing-script gap is a history lesson, not a current bug.
- KEEP: launchd (23:03). RETIRE: cron `45 23` line.

### 1.5 ale_recommendations.py, DEAD ON BOTH SURFACES, script does not exist
- crontab: `5 21` -> `/Users/TJ/.hermes/workspace/scripts/ale_recommendations.py` -> `ale-recommendations-cron.log`
- launchd `ai.hitnetwork.ale-recommendations`: 21:05, SAME missing script, SAME log
- EVIDENCE: `find` across `.hermes` and `hermes-workspace` confirms `ale_recommendations.py` exists NOWHERE on disk (only wiki output `.md` files with similar names remain). The shared log is wall-to-wall `python3: can't open file '.../ale_recommendations.py': [Errno 2] No such file or directory`. launchctl last-exit code = 2 (failure). Two schedulers fire 21:00/21:05 daily, both immediately error.
- VERDICT: DEAD on both surfaces. The script was deleted/moved; both schedulers are firing a ghost. This is dead weight generating error noise twice a day.
- RETIRE: BOTH the cron `5 21` line AND the launchd plist. Nothing to keep. (Note: `ale-pattern-detect` is the live ALE job, see table; do not confuse them.)

### Double-schedule resolution summary (keep launchd, retire cron, except 1.5)
- memory_distill.py: keep launchd 23:25; retire 3 cron lines; reconcile the two divergent script copies
- task_index_sync.py: keep launchd; retire cron `*/30`; THEN fix npx PATH + deployment-name bug
- memory-auto-indexer.py: keep launchd 23:15; retire cron `15 23`
- generate-memory.py: keep launchd 23:03; retire cron `45 23`
- ale_recommendations.py: retire BOTH (dead script)

Rationale for "keep launchd": launchd survives reboots cleanly, RunAtLoad self-heals, and StartInterval jobs auto-recover; crontab here is the legacy accretion layer that no prior audit saw. The exception is any TRUE daemon, which must stay launchd regardless.

---

## 2. Full Inventory: Every Entry, Schedule, Log, Liveness Verdict

Liveness rule: log mtime recent (last ~24h for daily jobs, or live PID for daemons) = ALIVE. Stale/missing/error-only = DEAD or BROKEN. "Age" measured from 2026-06-03 ~15:30.

### 2.1 CRONTAB (22 lines)
- task_index_sync.py: `*/30`; log task-index-sync-cron.log age 0h, 2.27MB. BROKEN (npx/deployment errors every run). Also double-sched (1.2).
- ale_pattern_detect.py: `0 21`; log ale-pattern-detect-cron.log age 18h. ALIVE (this is the live ALE pattern job; distinct from dead ale_recommendations).
- memory-auto-indexer.py: `15 23`; log memory-indexer.log age 16h. ALIVE. Double-sched (1.3).
- archiver.py (session-archive): `45 22`; log session-archive.log age 16h, 5.4MB. ALIVE.
- ale_recommendations.py: `5 21`; log ale-recommendations-cron.log age 18h. DEAD (script missing). Double-sched (1.5).
- memory_health.py: `50 20`; log memory-health-cron.log age 18h. ALIVE (note: distinct from launchd memory-health-check, see section 4).
- self-improvement-scanner.py: `50 22`; shares session-archive.log age 16h. ALIVE.
- generate-memory.py: `45 23`; log generate-memory.log age 15h. ALIVE. Double-sched (1.4).
- memory_distill.py: `50 23`; log distill-memory.log age 1h. ALIVE. Double-sched (1.1).
- memory_distill.py: `0 */2`; same log age 1h. ALIVE but OVER-SCHEDULED (13x/day for a nightly job). Double-sched (1.1).
- ingest-session-archives.py: `5 23`; log ingest-session-archives.log age 16h, 6MB. ALIVE.
- security-audit.py: `0 23`; log security-audit.log age 16h. ALIVE.
- corrections-to-skill.py: `0 22`; log corrections-to-skill.log age 17h. ALIVE.
- q4-to-skill.py: `0 22`; log q4-to-skill.log age 17h. ALIVE.
- detect-correction.py: `30 21`; log correction-detect.log age 18h. ALIVE.
- heartbeat.py: `*/15`; log heartbeat.log age 0h, 676KB. ALIVE.
- email-to-brain-cron.sh: `*/30`; no redirect (writes own log). UNVERIFIED here (no stdout path); presumed alive, recommend adding a log.
- ingest-sessions-to-brain.py --source jsonl: `*/30`; log ingest-sessions-to-brain.log age 0h, 45MB. ALIVE (log is large, candidate for rotation).
- ingest-sessions-to-brain.py --source archives: `20 * * * *`; same log age 0h. ALIVE.
- skill-check.py: `0 6` (6am ET); log skill-check.log age 9h. ALIVE.
- watchdog.sh (voice): `*/2`; output to /dev/null. Script EXISTS; voice daemons alive (section 5) so watchdog is functioning. ALIVE-by-proxy (no log = no direct evidence; see required change).
- hit-sie-patterns: `0 9 * * 2` (Tue 9am); log patterns.log age 28h. ALIVE (weekly, last ran on schedule).

### 2.2 LAUNCHD (35 active plists)
Daemons (KeepAlive, verified by live PID via `ps`):
- ai.hermes.gateway: PID 634, KeepAlive. log gateway.log age 0h, 3.7MB. ALIVE (core daemon).
- ai.hermes.gateway-watchdog: StartInterval 60. stdout log 0 bytes since May-12 BUT it is a watchdog (silent when healthy). Loaded. ALIVE-by-design.
- ai.hermes.heartbeat: StartInterval 60. stdout 0 bytes since May-12. Loaded. ALIVE-by-design (silent watchdog).
- ai.hitnetwork.tts-proxy: PID 1361, node, uptime 15d. KeepAlive. ALIVE (voice cluster).
- ai.hitnetwork.voice-server: PID 59038, node, uptime 8d. KeepAlive. health endpoint returns auth challenge = server up. ALIVE (voice cluster). Log quiet since May-31 is normal for an idle realtime bridge.
- ai.hitnetwork.voice-tunnel: PID 26109, cloudflared. log age 5h. KeepAlive. ALIVE (voice cluster).
- network.hitnetwork.ptt-daemon: PID 71910, uptime 15d. KeepAlive. ALIVE (voice cluster).
- com.gbrain.autopilot: PID 41645, KeepAlive. log age 0h, 33MB. ALIVE (log huge, rotate).
- com.tj.gbrain-mcp: PID 44225, bun serve :8787, KeepAlive. log mcp-out.log 0 bytes since Apr-29 (logs elsewhere). ALIVE (PID live).
- homebrew.mxcl.postgresql@17: PID 1350, KeepAlive. ALIVE.
- com.ollama.serve: KeepAlive, RunAtLoad. /tmp/ollama.log 0 bytes age 15h. Loaded; Ollama app also runs its own instance (see note). ALIVE-but-redundant (the Ollama.app GUI launches its own server; this plist may be a duplicate launcher).
- com.hermes.tailscale-keepalive: StartInterval 300. last-exit 127 (command-not-found), stdout 0 bytes since Apr-20. BROKEN (exit 127 = binary not found on PATH).
- pm2.TJ.plist: KeepAlive, RunAtLoad. /tmp/com.PM2.out MISSING. Owned by root. Loaded; pm2 resurrect. UNVERIFIED (out file absent); other arm owns pm2, defer.

Periodic launchd jobs (StartCalendarInterval / StartInterval, no KeepAlive):
- ai.hitnetwork.ale-memory-bridge: 23:15; log age 16h. ALIVE.
- ai.hitnetwork.ale-pattern-detect: 21:00; log age 18h (shares cron's ale-pattern-detect-cron.log). ALIVE but note: ale-pattern-detect runs in BOTH cron (`0 21`) and launchd (21:00) to the SAME log. SIXTH double-schedule, not in the original 5. Flagged below.
- ai.hitnetwork.ale-recommendations: 21:05. DEAD (script missing, last-exit 2). See 1.5.
- ai.hitnetwork.ale-session-sync: StartInterval 900; log age 26h. SUSPECT (15-min job, log 26h stale = likely stalled/erroring; investigate).
- ai.hitnetwork.coingecko-movers: 06:00; log age 9h. ALIVE.
- ai.hitnetwork.cron-monitor: 23:35; log age 15h. ALIVE.
- ai.hitnetwork.decision-extractor: 23:35; log age 15h. ALIVE.
- ai.hitnetwork.decision-to-ale: 23:45; log age 15h. ALIVE.
- ai.hitnetwork.generate-memory: 23:03; log age 15h. ALIVE. Double-sched (1.4).
- ai.hitnetwork.lock-check: 22:30; log age 17h, last-exit 2. ALIVE-WITH-NONZERO-EXIT (runs but exits 2; verify intended).
- ai.hitnetwork.memory-auto-indexer: 23:15; log age 16h. ALIVE. Double-sched (1.3).
- ai.hitnetwork.memory-distill: 23:25; log age 16h. ALIVE. Double-sched (1.1).
- ai.hitnetwork.memory-health-check: 23:31; log age 16h, last-exit 1. ALIVE-WITH-NONZERO-EXIT.
- ai.hitnetwork.nightly-auto-indexer: 23:00; log age 16h, last-exit 2. ALIVE-WITH-NONZERO-EXIT. Overlaps memory-auto-indexer (section 4).
- ai.hitnetwork.promotion-check: 23:05; log age 16h, last-exit 2. ALIVE-WITH-NONZERO-EXIT.
- ai.hitnetwork.reconcile-completed: 23:20; log age 16h, last-exit 2. ALIVE-WITH-NONZERO-EXIT.
- ai.hitnetwork.session-sync-morning: 08:00; log age 7h. ALIVE.
- ai.hitnetwork.task-index-sync: StartInterval 1800; log age 0h. BROKEN (see 1.2).
- ai.hitnetwork.voice-logrotate: 03:00; log age 12h (ran at 03:00 today). ALIVE (voice cluster).
- ai.hitnetwork.wal-checkpoint: 23:30; log age 16h, last-exit 2. ALIVE-WITH-NONZERO-EXIT.
- com.hitnetwork.ale-sweeper: StartInterval 900; log age 0h, 14MB. ALIVE (the HR-10 ALE backstop; log huge, rotate).
- com.hitnetwork.dc-sheets-sync: 11:00; log age 4h. ALIVE.

Note on launchctl exit codes: a non-zero last-exit (1 or 2) on the ai.hitnetwork.* nightly batch is widespread (lock-check, memory-health-check, nightly-auto-indexer, promotion-check, reconcile-completed, wal-checkpoint all show 1 or 2). Logs ARE fresh (16h, ran last night), so the scripts execute, but they signal failure exit codes. This is a monitoring smell: a fleet of nightly jobs that all exit non-zero will never trip a launchd-failure alert because there is no alerting path watching exit codes. Recommend a follow-up pass (not Arm B scope) to confirm each non-zero exit is intentional vs silent failure.

---

## 3. Dead-Script Detection (target missing or log error-only)

Confirmed dead (RETIRE):
- ale_recommendations.py: file does not exist on disk; both cron and launchd error every fire. DEAD. Retire cron line + plist.

Broken (script exists, runs, but produces only errors, treat as functionally dead until fixed):
- task_index_sync.py: every run ends in `FileNotFoundError: npx` + malformed Convex deployment name. 4,108 failed runs logged, 2.27MB of stack traces. Functionally dead output. Fix PATH + deployment name before keeping.

Dead dependency referenced by a live script:
- wiki-indexer.py: both memory-auto-indexer logs report `[WikiIndex] SKIP: wiki-indexer.py not found at /Users/TJ/.hermes/workspace/scripts/wiki-indexer.py`. The indexer runs but silently skips its wiki sub-step every night. Either restore wiki-indexer.py or remove the call.

Broken daemon:
- com.hermes.tailscale-keepalive: launchctl last-exit 127 (command not found). The keepalive binary/script is not resolvable on the launchd PATH. Tailscale itself runs via the macsys app (PID 721 seen in launchctl), so this keepalive is both broken AND likely redundant. Investigate.

Suspect (stale relative to its own cadence):
- ai.hitnetwork.ale-session-sync: 15-min job, log 26h stale. Either stalled or erroring without writing. Investigate.

Already retired/disabled (correctly out of scope, NOT touched):
- _retired-2026-05-15/: wiki-inbox-watcher, wiki-nightly-ingest (the wiki-indexer.py orphan above is likely fallout from this retirement).
- disabled/: ai.openclaw.gateway, ai.openclaw.lock-cleanup.
- .com.hitnetwork.auto-enrich.plist.disabled-2026-05-28 (dotfile, disabled).

---

## 4. Memory Subsystem Map (~8 jobs, overlap analysis)

The memory layer is the densest overlap zone. What each actually does, by log evidence:

- memory_distill.py (cron, Lex-Workspace copy): distills MEMORY.md. Fires 14x/day (13 from `0 */2` + 1 from `50 23`). Over-scheduled.
- memory_distill.py (launchd, .hermes copy): SAME logical job, DIFFERENT script copy, 1x/day at 23:25. The fork (section 1.1).
- memory-auto-indexer.py: indexes session files into the memory store. Fires 2x at 23:15 (cron + launchd, the race in 1.3). "Files skipped ~3855, Entities upserted 0."
- nightly-auto-indexer.py (launchd only, 23:00): a SECOND indexer running 15 min before memory-auto-indexer. Last-exit 2. Strong candidate for being a superseded predecessor of memory-auto-indexer. Two indexers at 23:00 and 23:15 doing overlapping work is almost certainly unintentional. Compare the two scripts and retire one.
- generate-memory.py: regenerates MEMORY.md.generated from 39K entities. Fires 2x/night (23:03 launchd + 23:45 cron, section 1.4). Idempotent, wasteful.
- memory_health.py (cron, 20:50): writes memory-health-cron.log. ALIVE.
- memory-health-check.py (launchd, 23:31): writes memory-health-check.log, last-exit 1. These are TWO DIFFERENT health scripts (underscore vs hyphen, different paths, different times, different logs). Classic name-variant duplication. Determine if both are needed or one is a stale fork.

Memory cluster verdict: the pipeline is generate -> index -> distill -> health, but it is run by TWO uncoordinated schedulers with at least 3 fork/duplicate pairs (distill x2 copies, indexer x2 schedulers + nightly-auto-indexer 3rd indexer, health x2 scripts). The intended nightly DAG is recoverable but currently fires 5-6 extra times against shared files (MEMORY.md, the entity store). Consolidation target: ONE scheduler (launchd or jobs.json), ONE script per stage, sequenced (not all crammed into 23:00-23:45 racing each other).

---

## 5. Voice-Server Cluster: Coherent Service

This is the one clean cluster on the surface. Verdict: COHERENT, well-formed service, leave intact.

- voice-server (launchd, KeepAlive): PID 59038, node, 8d uptime. The realtime bridge (server.mjs/openai_session.mjs per the cluster AGENTS.md). health endpoint at :8765 responds. ALIVE.
- voice-tunnel (launchd, KeepAlive): PID 26109, cloudflared named tunnel `lex-voice`. log age 5h. Exposes the server publicly for Twilio. ALIVE.
- tts-proxy (launchd, KeepAlive): PID 1361, node, 15d uptime. Text-to-speech proxy. ALIVE.
- ptt-daemon (launchd, KeepAlive): PID 71910, native PTTDaemon binary, 15d uptime. Push-to-talk. ALIVE.
- voice-logrotate (launchd, 03:00 daily): newsyslog rotation of voice logs. Ran today at 03:00. ALIVE.
- watchdog.sh (cron, */2): voice-server health watchdog. Script exists; the daemons it guards are all up, so it is functioning. Only gap: output goes to /dev/null, so no direct liveness evidence (see required change).

All five long-running pieces use KeepAlive with SuccessfulExit=false (correct daemon pattern), have real multi-day PIDs, and the rotation + watchdog round it out. This cluster is correctly on launchd (true daemons MUST stay launchd, never migrate to jobs.json). The only nit is the */2 watchdog living in cron while everything else is launchd; for consistency it could become a launchd StartInterval=120 job, but that is cosmetic, not a bug.

---

## 6. Migration Recommendation (jobs.json vs launchd vs cron)

Principle: launchd is correct for TRUE daemons; periodic batch scripts are candidates for unified governance under the Hermes scheduler (jobs.json); crontab is the unaudited legacy layer and should be drained.

KEEP ON LAUNCHD (true daemons, do NOT migrate):
- ai.hermes.gateway, gateway-watchdog, heartbeat
- voice cluster: voice-server, voice-tunnel, tts-proxy, ptt-daemon, voice-logrotate
- com.gbrain.autopilot, com.tj.gbrain-mcp, postgresql@17, com.ollama.serve, pm2

DRAIN CRONTAB (migrate the survivors to jobs.json for unified governance, after retiring the duplicates):
- All 5 double-scheduled cron lines: RETIRE (launchd already owns them).
- Remaining unique cron jobs (archiver, self-improvement-scanner, security-audit, corrections-to-skill, q4-to-skill, detect-correction, heartbeat.py, ingest-sessions-to-brain x2, skill-check, ale_pattern_detect, memory_health, hit-sie-patterns, ingest-session-archives, email-to-brain): these are periodic Python batch jobs with no daemon semantics. They are the right shape for jobs.json so the Hermes scheduler governs them with one source of truth, success/failure signals, and alerting (which the raw cron+launchd surface entirely lacks). Migrate in a controlled pass, one job at a time, soak-gated.

CONSOLIDATE THE NIGHTLY MEMORY DAG: pick ONE owner (recommend jobs.json for sequencing + governance, since these are batch not daemon), collapse the fork/duplicate pairs to one script per stage, and sequence generate -> index -> distill -> health instead of racing them in the 23:00-23:45 window.

Owner + reason for anything kept separate: voice cluster stays launchd (daemons), owner = voice-server AGENTS.md / SECURITY.md. gateway/gbrain/postgres/ollama/pm2 stay launchd (daemons), owner = respective service. Everything else has no daemon justification and should move to jobs.json.

CRITICAL SAFETY NOTE: A blind subtraction 4 days ago broke the system. Do NOT batch-unload. Migrate one job, soak it (confirm the new owner fires and the old surface is quiet via log mtime), then unload the old entry. cron-retirement-soak-gate methodology applies.

---

## 7. Dead-Weight Retire List (with evidence)

Retire only after the soak gate. Evidence cited per item.

1. crontab `5 21 ale_recommendations.py` AND launchd ai.hitnetwork.ale-recommendations: script does not exist on disk; logs are 100% file-not-found errors; last-exit 2. Pure dead weight firing 2x/day.
2. crontab duplicate of memory_distill (`50 23` + `0 */2`): launchd owns the canonical nightly run; the `0 */2` is also accidental 13x/day over-scheduling. Keep launchd, retire all 3 cron lines (after reconciling the two script copies).
3. crontab duplicate of task_index_sync (`*/30`): launchd owns it; cron is the duplicate. Retire cron, then fix the npx/deployment bug on the launchd copy (the job is broken on BOTH, but only one should exist before fixing).
4. crontab duplicate of memory-auto-indexer (`15 23`): launchd owns it; the 1-second-apart concurrent fire is a race. Retire cron.
5. crontab duplicate of generate-memory (`45 23`): launchd owns it; retire cron.
6. Candidate: nightly-auto-indexer (launchd, 23:00) vs memory-auto-indexer (23:15): two indexers 15 min apart, nightly-auto-indexer exits 2. Likely a superseded predecessor. Confirm by diffing the scripts, then retire the loser. Not yet confirmed dead, so this is INVESTIGATE-then-retire, not blind-retire.
7. Candidate: com.hermes.tailscale-keepalive: last-exit 127 (binary not found), redundant with the Tailscale macsys app. INVESTIGATE-then-retire.
8. Sixth double-schedule not in the original brief: ale_pattern_detect runs in BOTH cron (`0 21`) and launchd ai.hitnetwork.ale-pattern-detect (21:00) to the SAME log. Same resolution pattern: keep launchd, retire cron line. Flagging because the brief said "5 confirmed"; this is a 6th of the same class the prior audits missed.

---

## 8. Skill-Routing Note (lesson-hunter posture)

The class of bug here (one logical job scheduled on two independent scheduler surfaces, neither aware of the other) is exactly what `cron-liveness-audit-positive-assertion` and `cron-retirement-soak-gate` exist to catch, and both were loaded for this dispatch. Routing is correct. The gap is that NO prior audit enumerated launchd at all (`crontab -l` and `jobs.json` were checked; `~/Library/LaunchAgents` was invisible). Recommend the `maintain` / drift-audit cadence add a mandatory `ls ~/Library/LaunchAgents/*.plist` + `launchctl list` step so the shadow surface cannot stay invisible. That is a one-line addition to an existing skill, not a new skill. Filing this as: audit-scope was incomplete, not a missing lesson.

---

## Learnings

- macOS has at least SIX scheduler surfaces; crontab and launchd were invisible to every prior audit. Any "scheduler audit" that does not run `launchctl list` and enumerate `~/Library/LaunchAgents/*.plist` is structurally incomplete. Add it to the drift-audit checklist.
- launchctl list exit codes are a free, untapped failure signal. Six nightly ai.hitnetwork.* jobs exit non-zero (1 or 2) and nothing watches them. A monitoring standard (success signal, failure signal within 5 min, alerting path) is absent on this entire surface.
- Double-schedule detection MUST compare script PATH, not just script NAME. memory_distill double-fires from TWO DIFFERENT file copies; that is a fork, strictly worse than a duplicate, and invisible if you only diff job names.
- Liveness MUST be log-mtime/PID based, never schedule-based. ale_recommendations is "scheduled" twice daily and has been dead for the entire log history; the schedule lied, the log told the truth.
- KeepAlive daemons with quiet logs are NOT dead. voice-server's log was 74h stale but the PID has 8 days of uptime and the health endpoint answers. Verify daemons with `ps` + health check, not log mtime.
- Shared log files mask double-fires. memory-auto-indexer's two surfaces wrote to two different logs, which is the ONLY reason the 1-second-apart race was visible. task_index_sync and generate-memory share one log per pair, hiding the doubling until you count run-markers.
- The "5 confirmed double-schedules" was an undercount: ale_pattern_detect is a 6th of the same class. Confirmed counts from incomplete prior audits should be treated as lower bounds.

## Proof of Completion
- File written: /Users/TJ/.hermes/hermes-agent/tasks/plans/scheduler-audit-arm-b-shadow.md
- Evidence base: `crontab -l` (22 lines), `ls ~/Library/LaunchAgents` (35 active plists), PlistBuddy dump of every plist, `launchctl list` exit codes, `stat -f %m` on 46 log files, `ps -p` on 3 voice PIDs, `find` for ale_recommendations.py (absent), run-marker counts (task_index_sync 4108, generate-memory 80), and raw log tails for all 5 double-scheduled jobs.
- Changes made to the system: NONE. Read-only audit per the analysis-only constraint.
