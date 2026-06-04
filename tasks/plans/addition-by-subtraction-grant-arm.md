# Addition-by-Subtraction Audit (Grant arm, independent)

**Agent:** Grant (Sr. Systems Engineer, Hit Network engineering critic)
**Date:** 2026-06-03
**Mode:** FILE WRITE MODE (audit). Analysis + plan ONLY. Nothing deleted.
**Methodology:** gstack-investigate (root cause first, no symptom-fixing). Reality verified on disk, not from docs.
**Independence note:** I did not see any other agent's analysis. Conclusions are my own, formed from raw system state.

## FINAL OUTCOME (one line)
Done = a cited findings report proving WHERE Hit Network built a Foxconn factory, plus a prioritized consolidation plan whose centerpiece is shipping the missing subtraction loop (the structural dual of our ADD engines), not a deletion list.

## VERDICT

**APPROVED WITH CHANGES** to the stack's current shape. The over-scaffolding is real and Garry Tan's critique lands, but the root cause is NOT "we have 86 crons and 345 skills." The root cause is a structural one-way ratchet: **every proactive mandate in this system ADDS (skillify, Dreamer, SIE-proposer, MC Feature Suggester, the wiring-gate, "propose a skill if none exists"), and NO agent or cron owns SUBTRACTION.** The scaffolding accumulated because nothing was ever charged with asking "should this still exist?" The fix is one missing organ, not N deletions.

I stake my reputation on the root-cause finding. I stake my reputation on the verified fact that the subtraction mandate specced on 2026-05-30 never landed on disk.

---

## BASELINE (verified on disk 2026-06-03)

- `~/.hermes/cron/jobs.json`: **86 jobs** (85 enabled, 1 paused, 1 errored, 2 never-run). `updated_at` 2026-06-03T14:59 ET.
- `~/.hermes/skills/`: **345 SKILL.md** across 127 top dirs.
  - gstack-*: **45 dirs** (UPSTREAM-VENDORED, out of scope).
  - gbrain-*: **9 dirs** at top level (UPSTREAM-VENDORED, out of scope).
  - `~/.hermes/skills/hit-network/`: **122 SKILL.md** = the prunable surface.
- Guard/watchdog/audit/monitor-shaped crons: **28 of 86** (33%). This is Garry's exact "33 alarms" complaint, almost to the number.
- gbrain brain_score 91/100; gbrain health 6/10; `gbrain doctor` is a native command (verified: `gbrain doctor --help` returns usage).

---

## FINDING 1 (CRITICAL): The subtraction organ was specced and never shipped. The ratchet is still live.

This is the headline and it is verifiable on disk.

A prior system-wide over-engineering audit already ran on **2026-05-30** (4 days ago). Its artifact lives at:
`~/.hermes/skills/hit-network/debug-skill-bias-before-prompt/references/system-overengineering-audit-2026-05-30.md`

That audit reached the identical root cause I reached independently: "**no agent owned subtraction.** Grant ... had ZERO simplicity/elegance/anti-over-engineering language in his charter ... His entire posture was ADDITIVE." It concluded the correct fix was deliberately tiny: "**ONE weekly drift-audit bullet, not 4 charter additions.**" Framed as the dual of the wiring-gate: "the wiring-gate asks 'is this new thing connected?'; the subtraction scan asks the inverse: 'is this existing thing still connected?'"

**The fix never landed.** I read Grant's live charter at `~/hermes-workspace/Lex-Workspace/agents/grant/AGENT.md` (mtime 2026-05-20, which PRE-DATES the 2026-05-30 audit). Section 13 WEEKLY DRIFT AUDIT has 8 items (AGENT.md-vs-org-chart, skill-registry-vs-disk, model assignments, cron health, automation opportunities, monitoring gaps, org consistency, file-write discipline). **None of them is the subtraction scan.** `grep -inE 'subtract|prune|simpl|elegan|over.?engineer|still connected|minimal'` over the live AGENT.md returns zero hits in any mandate position.

Root-cause classification (per my charter's lesson-hunter posture): this is a **wiring-gate failure**. A lesson was learned (2026-05-30), a fix was specced (one bullet), and it was never persisted to the layer where it would fire (Grant's charter / the Sunday drift cron). The one-way ratchet that ACCUMULATED the Foxconn factory is still turning. Confidence: HIGH. Evidence: the spec file and the charter both exist on disk and contradict each other.

**This single finding explains the whole stack.** You don't have 86 crons because anyone wanted 86 crons. You have 86 because the system can only add and has never once been able to subtract.

---

## FINDING 2 (HIGH): Redundant supervision of subsystems that already self-report health.

Categorized all 86 crons by subsystem (counts are exact):

- GBrain: **19 crons**
- SIE: **13 crons**
- MC / Mission Control: **11 crons**
- Routing intel: **7 crons**
- Meet / Meeting: **6 crons**
- Lex self-review: **5 crons**
- Cron-scheduler self-supervision: **3 crons** (+1 Jobs.json Shrink Alarm = 4)
- Other: 22 crons

### 2a. GBrain is supervised by 7+ independent health crons while `gbrain doctor` exists natively.

GBrain has its own health surface (`gbrain doctor`, confirmed live). On top of it we run, as SEPARATE crons:
- GBrain Daily Health Check (9am)
- GBrain Brain-Growth Audit (daily 11am)
- GBrain Autopilot Health Audit (daily 11:05am)  ← fires 5 minutes after the previous one
- GBrain Export Watchdog (daily 06:00)
- GBrain Central-Node Audit (weekly Mon 09:00)
- GBrain Embed Safety-Net (every 15 min)
- GBrain Weekly Score Delta (Sat 7am)

Seven crons re-deriving a health picture the tool emits itself. The 11:00 and 11:05 audits are the clearest tell: two near-simultaneous daily health passes on the same subsystem. This is exactly Garry's "alarms set for a worker who shows up on time." Confidence: HIGH.

### 2b. The cron scheduler is watched by FOUR independent watchdogs.

- Cron Health Monitor (every 2h): "detect missed jobs and alert"
- Cron-Heartbeat Watchdog (every 4h): script `cron-heartbeat-watchdog.py`, silent-when-healthy
- Stale Cron Path Watcher (23:55): script `stale-cron-path-watcher.py`
- Jobs.json Shrink Alarm (every 30min): alarms if jobs.json shrinks

Four crons whose entire job is supervising the cron subsystem itself. A scheduler that needs four independent watchdogs to trust itself is the textbook Foxconn cage. They likely catch DISTINCT failure classes (missed runs vs heartbeat vs stale path vs accidental mass-delete), so this is a CONSOLIDATION target (4 watchers -> 1 supervisor with 4 checks), NOT a deletion target. Confidence: HIGH on the redundancy; MEDIUM on full collapsibility (needs the soak gate below to prove identical coverage).

### 2c. MC has overlapping pollers/staleness crons.

MC Approval Pending Poller (every 30min) + MC Approval Pending Mark Stale (daily 13:00) + MC Stuck in_progress Audit (daily 6am) + MC Drift Watchdog (hourly) + mc-healthcheck (every 5min). At least the two "approval pending" crons are candidates to fold into one poller that both surfaces and ages-out. Confidence: MEDIUM (needs MC schema read to confirm they touch the same table the same way).

---

## FINDING 3 (HIGH): The ADD engines all fire on cron. The SUBTRACT procedures fire only on human request.

The asymmetry is mechanical, not philosophical. The ADD side is automated; the SUBTRACT side is manual.

ADD engines, all cron-scheduled:
- Overnight Dreamer (10:30 PM daily)
- GBrain Native Dream (2am) / GBrain Dream Cycle (paused)
- sie-improvement-proposer-daily (6am)
- sie-skillify-weekly (Tue 10am)
- MC Feature Suggester (nightly proposer, 23:50)

SUBTRACT capability exists ONLY as passive skills with no scheduled trigger:
- `agent-retirement-audit` (hit-network skill)
- `cron-retirement-soak-gate` (hit-network skill)
- `card-retirement-knowledge-extraction` (hit-network skill)
- `file-consolidation`, `db-merge-consolidation`, `multi-pass-consolidation-protocol` (hit-network skills)

These are good skills. But a skill with no cron and no charter mandate fires only when a human remembers to ask. `grep` of all 86 cron prompts for `retire|prune|subtract|consolidat|cleanup` returns only ADD engines plus `sie-promote-token-cleanup` (token GC, not structural retirement). **There is no scheduled subtraction pass anywhere in the stack.** Confidence: HIGH.

---

## FINDING 4 (MEDIUM): Confirmed dead weight and confirmed clean consolidations (de-risking both directions).

I verified specific claims rather than assuming.

**Clean consolidation (good news, do not re-litigate):** `gbrain-link-recovery` claims it absorbed ~25 source skills. I checked: only THREE link-related dirs exist in hit-network (`gbrain-link-rebuild`, `gbrain-link-rebuild-daily`, `fetch-reachability-pivot`), all distinct legitimate functions. The 25 saturation-routing variants are NOT lingering as separate dirs. That consolidation shipped cleanly. This is the PROOF that consolidation-done-right works and is the model to replicate.

**Actual dead weight found:**
- `~/.hermes/skills/task-skills-v15-backup/` is a top-level backup dir of loose `.md` files (ai-avatar.md, ai-video-production.md, etc.), not even SKILL.md format. Pure stale snapshot. Candidate for archive-and-soak.
- GBrain Dream Cycle cron is PAUSED while GBrain Native Dream runs (the May 1 incident codified in `cron-retirement-soak-gate`). A paused-superseded cron sitting in jobs.json is exactly the "superseded-but-loaded" signature. Candidate for retirement THROUGH the soak gate (it already has a 7-day-soak skill written for precisely this).

Confidence: HIGH on task-skills-v15-backup being dead; MEDIUM on Dream Cycle (verify Native Dream produces equal-or-higher timeline entries before retiring, per the soak gate's own May 1 rule).

---

## FINDING 5 (CRITICAL RISK CONTEXT): The last "addition by subtraction" attempt caused a P1-class regression.

This is the single most important de-risking fact and it is recent and on-disk.

Documented in `~/.hermes/skills/hit-network/prompt-compiler-operations/SKILL.md` (lines ~583-587): the 2026-05-30 weekend subtraction work shipped a commit (`a745b21`, Fri 2026-05-29) that, alongside a correctly flag-gated selector, ALSO changed the LIVE keyword matcher defaults un-gated: `relevance_floor 0.4->0.6` and `top_n 25->7`. Result: **every dispatch since that Friday injected ~72% fewer skills and culled borderline-relevant ones** (the full design suite dropped from a deck dispatch). TJ's words: "we tried to do addition by subtraction last week and it seems we've broken proper skills injection."

The lesson is blunt: **blind subtraction in this stack has already drawn blood once, 4 days ago.** Any plan that proposes cutting must route through a soak gate and a positive-assertion liveness check, never `rm`. Confidence: HIGH.

---

## ROOT CAUSE (gstack-investigate, single sentence)

The Foxconn factory accumulated because Hit Network's improvement loop is structurally one-directional: skillify/Dreamer/SIE-proposer/Feature-Suggester and the wiring-gate all ADD and all run on cron, while the only subtraction capability lives in passive skills with no scheduled trigger and no charter mandate; the dual mandate that would close the loop was specced on 2026-05-30 but never written to disk, so the ratchet has never once reversed.

Everything downstream (28 guard crons, 7 redundant GBrain health passes, 4 cron-scheduler watchdogs, stale backup dirs, the paused-but-present Dream Cycle) is a SYMPTOM of that single structural gap. Fixing symptoms without fixing the ratchet guarantees re-accumulation.

---

## PROPOSED PLAN (prioritized; consolidation and a built loop over deletion)

Constraint reminder: nothing deletes in this plan. Every actual prune later goes through TJ approval. Every cut routes through the existing `cron-retirement-soak-gate` (7-day soak, identical-output proof) and `cron-liveness-audit-positive-assertion` skills.

### Phase 0 (DO FIRST, smallest possible change): Ship the missing organ.
This is the leanest change that fixes the root cause. Resist over-engineering the anti-over-engineering fix.

1. **Land the subtraction bullet that never shipped.** Add ONE item to Grant's AGENT.md Section 13 WEEKLY DRIFT AUDIT: the subtraction scan, framed as the dual of the wiring-gate. "For each cron/skill/script: is this existing thing still firing, still read, and still distinct from a sibling? Flag-only output; propose retirements through the soak gate; never auto-delete." Use EXISTING issue categories (the `## Issues` YAML taxonomy already in AGENT.md, e.g. add candidates under `architecture` / `scope-creep`). Do NOT add a new taxonomy bucket. Do NOT add a new cron. It folds into the Sunday drift audit that already runs.
2. **Wire it to fire.** Confirm the Sunday Lex drift cron actually invokes Grant's Section 13 and that Grant's compiled prompt loads `agent-retirement-audit` + `cron-retirement-soak-gate` for drift-audit task types. (My OWN compiled prompt for THIS task loaded both, plus `cron-liveness-audit-positive-assertion`; verify the Sunday cron does too. If not, that is a skill-routing-broken finding to fix in the scanner triggers, not the role file.)

Acceptance: `grep subtract` on the live AGENT.md returns the new bullet; the next Sunday drift run emits a "subtraction candidates" section. Effort: ~1 hour. Risk: near-zero (additive to a charter, flag-only output).

### Phase 1: Consolidate the GBrain health crons (7+ -> 1 supervisor).
1. Build/confirm one GBrain Supervisor cron that runs `gbrain doctor` and surfaces its native output, plus the few checks doctor does NOT cover (export freshness, central-node, score-delta).
2. Soak-gate the redundant 7 against it for 7 days (per `cron-retirement-soak-gate`): the supervisor must surface every failure the 7 individually caught, at equal-or-higher rate, before any of the 7 is proposed for retirement.
3. Merge the 11:00 Brain-Growth Audit and 11:05 Autopilot Health Audit immediately (5-minutes-apart same-subsystem passes; lowest-risk merge).

Acceptance: one supervisor cron, soak log proving coverage parity, retirement proposals filed to TJ (not executed). Effort: 1-2 days. Risk: MEDIUM. **Single-point-of-failure risk:** collapsing 7 watchers into 1 means if the supervisor silently dies, all GBrain health visibility dies with it. MITIGATION: the supervisor MUST be covered by the cron-scheduler heartbeat (Phase 2) and must use positive-assertion liveness (emit a heartbeat row even when healthy, so silence = alarm), per `cron-liveness-audit-positive-assertion`.

### Phase 2: Consolidate the 4 cron-scheduler watchdogs (4 -> 1).
1. Enumerate the distinct failure class each of the 4 catches (missed-run, heartbeat-gap, stale-path, jobs.json-shrink).
2. Build one Cron Supervisor that runs all 4 checks in one pass, positive-assertion (heartbeat row even when clean).
3. Soak-gate 4 -> 1.

Acceptance: one supervisor, 4 checks, soak parity log. Effort: 1 day. Risk: HIGH on this one specifically. **SPOF risk:** this IS the watcher-of-watchers; if it dies silently nothing notices. MITIGATION: it must be the ONE cron that is externally monitored (a launchd dead-man timer or an MC healthcheck), never self-monitored. Do not collapse to 1 until that external dead-man exists. This is the one place where reducing redundancy could remove something load-bearing; treat it as the highest-care item.

### Phase 3: Consolidate MC pollers.
Fold MC Approval Pending Poller + MC Approval Pending Mark Stale into one poll-and-age cron after confirming (via MC schema read) they touch the same table the same way. Effort: half a day. Risk: LOW-MEDIUM.

### Phase 4: Archive confirmed dead weight (through soak, not rm).
1. `git mv` `~/.hermes/skills/task-skills-v15-backup/` to a `_deprecated/` location, soak 72h, then propose deletion to TJ.
2. Retire the paused GBrain Dream Cycle cron THROUGH its own soak gate: prove GBrain Native Dream produces equal-or-higher timeline entries (the exact May 1 check) before proposing removal.

Acceptance: archive moves logged, soak clean, TJ-approval requests filed. Effort: half a day. Risk: LOW (move-don't-delete + soak).

### Phase 5 (optional, only if Phases 0-4 prove the model): Promote the subtraction scan from flag-only to a standing weekly proposer.
ONLY after the Sunday drift subtraction scan has fired on real data and produced at least one good catch. Then, and only then, consider whether it deserves to be the symmetric dual of sie-improvement-proposer-daily (an explicit "retirement-proposer" that files candidate cards). Do NOT build this preemptively. The lean version (Phase 0 bullet) must earn its promotion. Building a retirement ENGINE before the retirement BULLET has proven itself would itself be the Foxconn-factory anti-pattern.

---

## HONEST RISKS

1. **Collapsing redundant watchers creates SPOFs.** The most dangerous moment in this whole plan is the instant 7-GBrain-watchers becomes 1 and 4-cron-watchdogs becomes 1. A silently-dead supervisor takes down ALL the visibility it consolidated. This is mitigated ONLY by positive-assertion liveness (heartbeat-when-healthy so silence alarms) plus an external dead-man on the watcher-of-watchers. Do not execute any collapse until that liveness scaffold exists. Yes, that means we ADD one small thing (a dead-man) to enable subtracting four. That is correct addition-by-subtraction, not contradiction.

2. **Blind subtraction has already drawn blood (Finding 5).** Four days ago a subtraction commit cut skill injection 72% and broke dispatches. The soak gate exists BECAUSE of incidents like this. Honor it. No `rm`. Move-and-soak only. TJ approval on every actual prune.

3. **"Grep-confirmed orphan" is not proof of death.** A cron prompt body can shell out to a script; a launchd plist can reference a differently-named binary; a "dead" script can be alive as a reference pattern. Verify all invocation paths before proposing any retirement. (The 2026-05-30 audit's own de-risking checklist documents this; reuse it.)

4. **Some redundancy is intentional defense-in-depth.** Four cron watchdogs MIGHT each catch a genuinely distinct failure mode. The soak gate's job is to PROVE coverage parity before collapse. If the soak shows the supervisor misses a class, the redundancy stays. Subtraction is a hypothesis to be tested, not a goal to be hit.

5. **The vendored line is load-bearing.** gstack-* (45) and gbrain-* (9) are Garry's own upstream skills. They are explicitly OUT of scope. Do not touch them; pruning upstream-owned skills would break the fork-integration contract and is not ours to do.

---

## WHAT GARRY-LEVEL ELEGANCE ACTUALLY LOOKS LIKE HERE

Not "86 crons becomes 40." The number is downstream. Elegance is: **the improvement loop becomes bidirectional.** Today the system can only grow. After Phase 0 it can also shrink, and shrinking runs on the same cadence growing does. Once the ratchet reverses, the guard count finds its own floor: redundant supervisors get flagged weekly and proposed for soak-gated retirement, dead backups get archived, and new scaffolding has to justify its existence against a standing "is this still connected?" scan. The N goes down as a CONSEQUENCE of fixing the structure, not as the goal. That is the difference between deleting alarms and retiring the need for them.

---

## 📊 Proof

- Output file: `/Users/TJ/.hermes/hermes-agent/tasks/plans/addition-by-subtraction-grant-arm.md` (this file).
- Cron count verified: `python3 -c "import json; print(len(json.load(open('~/.hermes/cron/jobs.json'))['jobs']))"` -> 86.
- Skill count verified: `find ~/.hermes/skills -name SKILL.md -not -path '*/.git/*' | wc -l` -> 345; hit-network subset -> 122; gstack -> 45; gbrain -> 9.
- Guard-shaped crons: 28 of 86 (regex match on name), enumerated in Finding 2.
- `gbrain doctor --help` returns usage (native health surface confirmed).
- Prior audit file read in full: `.../debug-skill-bias-before-prompt/references/system-overengineering-audit-2026-05-30.md`.
- Grant AGENT.md Section 13 read (lines 130-142): 8 drift items, zero subtraction mandate. mtime 2026-05-20 (pre-dates the 2026-05-30 spec) = fix never landed.
- Regression evidence: `prompt-compiler-operations/SKILL.md` lines 583-587 (floor 0.4->0.6, top_n 25->7, un-gated).

## Learnings

- **Wiring-gate failures hide in plain sight in the gap between a spec file and a charter file.** The single highest-value thing I did was diff the dates: a fix specced 2026-05-30 against a charter last touched 2026-05-20. The fix logically could not be in there. Always check mtimes when a doc claims a fix shipped. This is the verify-reality-not-docs rule paying off directly.
- **A skill with no cron and no charter mandate is not a capability; it is a hope.** Hit-network has excellent retirement skills (agent-retirement-audit, cron-retirement-soak-gate). They have never fired on cron. Capability that only activates on human recall is structurally equivalent to absent capability for the purpose of fighting accretion.
- **The right response to "you have too many guardrails" is almost never "delete guardrails."** It is "find the one missing guardrail that would have prevented the over-accumulation" (here: the subtraction scan) and "consolidate N-into-1 behind a soak gate." Blind deletion already broke this exact stack 4 days ago.
- **Resist over-engineering the anti-over-engineering fix.** The 2026-05-30 audit's own best insight was that the fix collapsed from 4 charter additions to 1 bullet under challenge, and that convergence-toward-less was the tell the method worked. My Phase 5 deliberately refuses to build a retirement ENGINE until the retirement BULLET earns it. Building the symmetric engine preemptively would itself be the Foxconn anti-pattern.
- **Lesson-hunter routing check (my charter):** the subtraction lesson exists (the 2026-05-30 file) but is not consumed (not in the live charter, not in any cron). Per my own rule, that makes this "skill/lesson routing is broken," and the fix belongs in the charter + scanner triggers, not buried in another reference doc. Filing it as Phase 0.
