# Breathe CLI — Issues & Ideas

## Done

### ~~1. Audio cues drift out of sync with breath cycle~~ FIXED
Phase boundaries now use ideal offsets anchored to `session_start`
(`next_boundary` variable) instead of `time.monotonic()` at phase
start. Eliminates cumulative sleep overshoot drift.

### ~~2. Time-of-day-aware default preset~~ DONE (v1.2)
Auto-selects preset by time of day when invoked with no arguments.

### ~~9. Session logging to disk~~ DONE (v1.3)
Append-only CSV at `~/.breathe_log.csv`. Spec §5.7. Flags:
`--log` (show path), `--no-log` (suppress for one session).

## Bugs

### 10. End-of-session rendering glitch
On session completion the loop breaks without rendering a final frame.
The bar and countdown freeze at their last state (e.g. bar at ~90%,
countdown at 00:01) before the session summary appears. Minor visual
annoyance, not a logic bug.

### 6. Sound cues play in wrong location
Sound cues are triggering but seem misattributed or misplaced.
Needs investigation and fix.

## Enhancements

### 3. README.md
Add a `README.md` with:
- App functionality and usage (install, presets, flags, runtime keys)
- A science section covering the clinical rationale: resonance
  breathing at 6 bpm, vagal tone, HFrEF context, Bernardi protocol
  references

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

### 8. Session progress bar (cycle count)
Add a second horizontal bar below the breath bar that tracks
cycle-count progress (completed cycles / total expected cycles).
Same width as the breath bar, identical visual style, but fills
gradually based on breath count rather than phase. Separate the
two bars with ~5 px (blank lines or spacing) so they're close
but visually distinct. Requires adjusting layout row calculations.
Note: this is related to but distinct from enhancement #4 (which
tracks elapsed time); this one tracks completed breath cycles.
