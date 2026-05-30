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

### 13. Countdown hits 00:00 one exhale-phase early
The countdown timer in the header reaches 00:00 at the end of the last
INHALE and stays at 00:00 throughout the entire last EXHALE (5–6 s of
breathing remain). The progress bar fills correctly — the two are out
of sync.

**Root cause (not yet identified):** the displayed remaining time
"runs too quickly" relative to the progress bar even though both
derive from `elapsed_display`. The counter reaches `duration_s`
one `exhale_s` before the session actually ends. This implies the
remaining-time calculation accumulates a full phase of error over
the session, but the exact mechanism is unclear.

**Desired behaviour:** the countdown ticks smoothly second by second,
reaches 00:00 at the exact moment the session ends (last exhale
completes), and snaps to an exact multiple of `cycle_s` on
pause → resume.

**Failed fixes (v1.6):**
1. *Ceil rounding in `format_mmss`* — changed `int()` to ceiling.
   Made each displayed second 1 s too high (e.g. 36 instead of 35).
   Did not fix the early-zero problem.
2. *Fall-through from PAUSED* — eliminated stale paused frame on
   resume by falling through to active code instead of rendering
   one more paused frame + continue. Reduced visual glitch but did
   not fix the early-zero problem.
3. *Stepped countdown (phase-boundary only)* — replaced smooth
   countdown with a value that only changed at phase transitions
   (`duration_s - breathing_base` during INHALE, minus `inhale_s`
   during EXHALE). Removed the smooth tick the user wants; still
   showed zero one phase early.
4. *`int(phase_elapsed)` for countdown* — used floor of complete
   seconds instead of raw float for the countdown while keeping
   smooth float for the progress bar. Counter ticks smoothly again
   but still hits 00:00 at end of last inhale.

All four attempts addressed display rounding without fixing the
underlying calculation. The remaining-time value itself is wrong
by the time the last cycle begins.

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
