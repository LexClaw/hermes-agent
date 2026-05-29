# Fix Cron Inactivity Timeout Killing delegate_task Subagents

**Card:** kn763nte9xzs64t61zay0f8am587n8c2
**Scope:** hermes-agent repo (`~/.hermes/hermes-agent/`)
**Status:** ✅ IMPLEMENTED — commit `1b2d95963`, pushed to main

## Problem

Cron jobs with `delegate_task` subagents are constantly timing out. The 600s inactivity timer on the parent cron agent fires because it doesn't properly track child subagent activity. The existing heartbeat in `tools/delegate_tool.py` (`_touch_activity` every 30s) is best-effort (catches all exceptions, silent failure) and stops touching when children go stale. Additionally, `child_timeout_seconds` (600s default) kills reasoning models on complex chains that need >10 min.

## Root Cause Analysis

1. **Parent timer doesn't know about children** — `cron/scheduler.py` line ~1687 polls `agent.get_activity_summary()` on the parent only. If the parent delegates and sits still, inactivity clock fires.
2. **Heartbeat stops on child stasis** — `tools/delegate_tool.py` line ~1424: if child doesn't advance iteration/tool for 15 cycles (450s idle) or 40 cycles (1200s in-tool), heartbeat thread breaks and parent goes dark.
3. **600s child timeout insufficient for reasoning models** — Opus/Sonnet 4 on complex reasoning chains (file ops + web fetches + synthesis) routinely exceed 10 min wall-clock.

## Existing Mitigations (already merged)

- `d6ef7fdf9`: Replaced wall-clock cron timeout with inactivity-based (April 5, 2026)
- `fcc05284f`: Added heartbeat + stale detection to delegate_tool (April 2026)
- `50d97edbe`: Bumped child_timeout_seconds from 300s → 600s (April 23, 2026)
- `0cc63043e`: Increased heartbeat stale thresholds (15 cycles idle / 40 in-tool)

## Fix (Three Phases)

### Phase 1: Immediate Config Fix (no code change)

Add to `~/.hermes/config.yaml` under the `delegation` and `cron` sections:

```yaml
cron:
  timeout_seconds: 0  # unlimited inactivity timeout for cron parent

delegation:
  child_timeout_seconds: 1800  # 30 min per child instead of 10 min
```

**Why this works:** The inactivity timer was 600s — with 0, the parent never times out on inactivity. The child still has a safety net at 30 min. Reasoning models on long chains get breathing room.

**Risk:** Without a parent timeout, a truly hung job with no child (or where heartbeat silently fails) runs forever. The `ale-sweeper` at 30 min remains the backstop.

### Phase 2: Structural Fix — Cron Scheduler Sees Delegation Activity

**File:** `cron/scheduler.py`, ~lines 1673-1696 (the inactivity poll loop)

Current code checks `agent.get_activity_summary()` on the parent agent. The fix:

1. Add a method or attribute on `AIAgent` like `has_active_children` or check if `_delegates` / child registry has running entries.
2. In the cron poll loop, if parent has active children, skip the inactivity check (treat it as "still active").
3. The `ale-sweeper` (30 min backstop) + `child_timeout_seconds` (30 min per child) remain as safety nets.

**Implementation:**
- Import `_get_active_children` or equivalent from the delegate_tool registry (line ~1459-1481 already tracks `_register_subagent` with status="running").
- Add import/usage of `_active_subagents` registry in scheduler's poll loop.
- When children exist: set `_idle_secs = 0` to prevent timeout.

### Phase 3: Harden the Heartbeat

**File:** `tools/delegate_tool.py`

1. Replace silent `except Exception: pass` on `_touch_activity` with `logger.warning` so failures are visible.
2. Make stale thresholds configurable via env/config rather than hardcoded constants at lines 522-523.
3. Add a "heartbeat still alive" log line at WARN level when heartbeat stops (the `break` at line 1432), so logs show exactly when the parent went dark.

## Test Plan

1. **Unit test** — `tests/cron/test_cron_inactivity_timeout.py` already covers the poll loop. Add a test case that simulates delegation activity and verifies the scheduler doesn't fire.
2. **Smoke test** — Create a cron job that delegates a subagent to do a 2-minute web search + synthesis task. Verify it completes without timing out.
3. **Config verification** — `HERMES_CRON_TIMEOUT=0` and `delegation.child_timeout_seconds: 1800` both parse correctly from env/config paths.

## Files Changed

| File | Change |
|------|--------|
| `cron/scheduler.py` | Add delegation-aware inactivity check in poll loop |
| `tools/delegate_tool.py` | Harden heartbeat logging, make thresholds configurable |
| `~/.hermes/config.yaml` | `cron.timeout_seconds: 0`, `delegation.child_timeout_seconds: 1800` |
| `tests/cron/test_cron_inactivity_timeout.py` | New delegation-activity test case |

## Notes

- The `ale-sweeper` (launchd job `com.hitnetwork.ale-sweeper`, 900s interval, 30 min threshold) is the structural backstop — it doesn't change.
- After Phase 1 is applied, the system is immediately more resilient even before Phases 2-3 ship.
- Grok analysis at https://grok.com/share/bGVnYWN5_7cbc0623-3d3b-470a-9b16-c699efc4e496 confirms the diagnosis.
