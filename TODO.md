# Breathe CLI — Issues & Ideas

## Done

### ~~1. Audio cues drift out of sync with breath cycle~~ FIXED
Phase boundaries now use ideal offsets anchored to `session_start`
(`next_boundary` variable) instead of `time.monotonic()` at phase
start. Eliminates cumulative sleep overshoot drift.

### ~~2. Time-of-day-aware default preset~~ DONE (v1.2)
Auto-selects preset by time of day when invoked with no arguments.

### ~~6, 10, 12. Bug fixes and audio refactor~~ DONE (v1.6)
Fixed sound cue sync (render new phase on transition frame), end-of-
session rendering (final frame + 400ms hold), and inhale bar one
segment short (`int` → `round`). Removed AudioToolbox ctypes fallback
(silently fails on Mojave); afplay is now the sole audio backend.
Consolidated summary/log pct/status calculation. 711 → 646 lines.

### ~~9. Session logging to disk~~ DONE (v1.3)
Append-only CSV at `~/.breathe_log.csv`. Spec §5.7. Flags:
`--log` (show path), `--no-log` (suppress for one session).

## Enhancements

### ~~3. README.md~~ DONE (v1.6)
Usage docs, clinical rationale (Bernardi, RSA, HFrEF), design
choices, presets/flags/runtime keys, session logging, safety.

### ~~4. Session progress bar (time-based)~~ DONE (v1.6)
Dimmed thin bar (`━`/`─`) below the breath bar, fills based on
`elapsed / duration_s`. Separate `progress_row` in layout.

### ~~5. Shorter phase labels~~ DONE (v1.6)
`INHALE`/`EXHALE` → `IN`/`OUT` via `PHASE_LABEL` map. Centering
uses label length, not state constant length.

### ~~7. Replace count-up timer with countdown~~ DONE (v1.4)
Header now shows remaining time counting down instead of elapsed/total.

### ~~11. State machine refactor and pause-resume reset~~ DONE (v1.5)
Replaced triple-nested render loop with flat state machine
(INHALE/EXHALE/PAUSED). Resume from pause restarts cycle from INHALE.
Countdown tracks completed breathing time only. Pause indicator
changed from ⏸ to ‖ (U+2016) to fix bracket shift.

### ~~13. Countdown hits 00:00 one exhale-phase early~~ FIXED (v1.7)
Root cause: `duration_s` was not always a multiple of `cycle_s`.
The session runs `ceil(duration/cycle)` full cycles, but the
countdown counted down from the raw `duration_s`. Fix: round
`duration_s` up to a whole number of cycles at config time.

### 8. Session progress bar (cycle count)
Add a second horizontal bar below the breath bar that tracks
cycle-count progress (completed cycles / total expected cycles).
Same width as the breath bar, identical visual style, but fills
gradually based on breath count rather than phase. Separate the
two bars with ~5 px (blank lines or spacing) so they're close
but visually distinct. Requires adjusting layout row calculations.
Note: this is related to but distinct from enhancement #4 (which
tracks elapsed time); this one tracks completed breath cycles.

### 14. Breathing modes beyond vagal tone
Broaden the app to support multiple breathing purposes (e.g. focus,
relaxation, box breathing) as distinct modes. Current safety
guardrails (no retention, no rapid breathing, ≥8s cycle) apply to
the vagal/HFrEF mode only. Other modes would define their own
constraints — e.g. box breathing would allow holds but enforce its
own limits. This is a significant architectural change: mode
selection, per-mode presets, per-mode guardrails, and updated
safety messaging. The single-file constraint may become the
binding limit.
