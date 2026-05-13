# Breathe CLI — Issues & Ideas

## Bugs

### ~~1. Audio cues drift out of sync with breath cycle~~ FIXED
Phase boundaries now use ideal offsets anchored to `session_start`
(`next_boundary` variable) instead of `time.monotonic()` at phase
start. Eliminates cumulative sleep overshoot drift.

## Enhancements

### 2. Time-of-day-aware default preset
Detect time of day from the system clock and default to a different
preset instead of always using `morning`. For example:
- Before noon → `morning` (10 min, 5-5)
- Noon to 18:00 → `morning` (or a future `midday` preset)
- After 18:00 → `evening` (15 min, 4-6)

This keeps the zero-argument invocation frictionless while matching
the session to the user's likely intent.

### 3. README.md
Add a `README.md` with:
- App functionality and usage (install, presets, flags, runtime keys)
- A science section covering the clinical rationale: resonance
  breathing at 6 bpm, vagal tone, HFrEF context, Bernardi protocol
  references

### 4. Session progress bar
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
