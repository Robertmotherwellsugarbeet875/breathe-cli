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

### 4. Session progress bar (time-based)
Add a second horizontal bar below the breath bar that shows overall
session progress (elapsed / total duration). Same width as the breath
bar. Needs careful design to avoid cluttering the minimal interface —
should be visually distinct (e.g. dimmed, different character) so it
doesn't compete with the breath bar for attention. Requires adjusting
the layout row calculations.

### 5. Shorter phase labels
Change `INHALE` / `EXHALE` to `IN` / `OUT`. Quieter, less clinical,
matches the minimal aesthetic. Verify the horizontal centering still
looks right with the shorter strings.

### ~~7. Replace count-up timer with countdown~~ DONE (v1.4)
Header now shows remaining time counting down instead of elapsed/total.

### ~~11. State machine refactor and pause-resume reset~~ DONE (v1.5)
Replaced triple-nested render loop with flat state machine
(INHALE/EXHALE/PAUSED). Resume from pause restarts cycle from INHALE.
Countdown tracks completed breathing time only. Pause indicator
changed from ⏸ to ‖ (U+2016) to fix bracket shift.

### 8. Session progress bar (cycle count)
Add a second horizontal bar below the breath bar that tracks
cycle-count progress (completed cycles / total expected cycles).
Same width as the breath bar, identical visual style, but fills
gradually based on breath count rather than phase. Separate the
two bars with ~5 px (blank lines or spacing) so they're close
but visually distinct. Requires adjusting layout row calculations.
Note: this is related to but distinct from enhancement #4 (which
tracks elapsed time); this one tracks completed breath cycles.
