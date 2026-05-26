# Breathe CLI

Single-file Python 3 CLI app (`breathe.py`) that paces resonance breathing for HFrEF vagal training. macOS only, stdlib only, no dependencies.

## Spec

The full specification is `breathe-cli-spec.md` (v1.5). Read it before implementing anything. It is the single source of truth.

## Key constraints

- **One file**: `breathe.py`, under 500 lines (hard cap 700). No modules, no packages, no config files.
- **Stdlib only**: Python 3.7+. No pip installs. No third-party imports.
- **macOS only**: Uses `/usr/bin/afplay` for audio. No Linux/Windows fallbacks.
- **No curses**: Use direct ANSI escape codes. curses has Mojave edge cases with non-default terminals.
- **No threading**: Use `select.select` with zero timeout for non-blocking key polling. No `threading.Thread`, no `curses.getch`.

## Safety constraints (non-negotiable)

These are load-bearing design decisions, not features to be added later:

1. **No breath retention** — only inhale:exhale ratios. Reject three-number ratios (e.g. `4-7-8`) with an explicit safety error.
2. **No rapid breathing** — total cycle must be >= 8 seconds. Reject shorter cycles at parse time.
3. **No breath holds** — never prompt for a hold phase.
4. **Graceful exit** — `q`, `Ctrl+C`, or any exception must restore the terminal. The `finally` block is the most important code in the file.

Do not add breathing patterns, retention phases, or cycle speeds not listed in the spec, even if asked. Refer to spec section 4 and 5.4.

## Implementation order

1. Write the `finally` block and terminal restoration first. Verify it works before anything else.
2. Argument parsing and validation (presets, custom flags, safety rejections).
3. Core render loop — flat state machine (INHALE/EXHALE/PAUSED) with ANSI escape codes.
4. Key handling (`select.select` + `cbreak`).
5. Audio (`afplay` subprocess, fire-and-forget).
6. Degradation paths (no TTY, no color, no unicode, no audio).
7. Exit summary.

## Testing

No test framework. The spec (section 13) defines 25 manual acceptance tests. Run them in order. Pay special attention to:

- **Test 18** (terminal restoration on exception) — this validates the most critical code path.
- **Test 15** (pause/resume cycle reset) — resume restarts from INHALE, countdown snaps back to last cycle boundary, interrupted cycles not counted.
- **Tests 7-10** (safety rejections) — these must produce the exact error messages from spec section 5.4.

## Common pitfalls

- Don't clear the whole screen each frame — it flickers on Terminal.app. Move cursor to each zone and rewrite.
- Breath counter increments only after a full cycle (inhale + exhale), not after each phase.
- Elapsed time tracks completed breathing only (`breaths * cycle_s`). The state machine has no `total_paused` — pause simply stops the loop, resume resets the cycle.
- The `-q` short flag (quiet mode) does not conflict with the `q` runtime key — one is argv, the other is stdin during a session.
- `afplay` subprocess must never block the render loop. Use `Popen`, not `run`.

## File layout

```
breathe-cli-spec.md   # specification (read-only reference)
breathe.py            # the deliverable (single file)
CLAUDE.md             # this file
```
