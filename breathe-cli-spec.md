---
title: 'Breathe CLI — Specification'
subtitle: 'A paced-breathing terminal app for HFrEF vagal training'
author: 'Marek Kowalczyk (spec by Claude, for Claude Opus 4.6)'
date: 2026-04-20
version: 1.2
target_platform: 'macOS 10.14.6 (Mojave)'
target_runtime: 'Python 3.7+ stdlib only'
status: 'ready to implement'
---

## 1. Executive summary

Build a single-file Python 3 command-line app named `breathe` that paces
resonance breathing at 6 breaths per minute for HFrEF vagal training. It
renders a minimal animated visual in the terminal, plays soft audio cues
at breath transitions, supports three named presets plus custom
durations and ratios, and exits cleanly at any time.

One file (`breathe.py`), standard library only, no pip installs, runs on
the user's Mojave Mac with whatever Python 3.7+ is on `PATH`.

## 2. Context and motivation

The user is a 54-year-old HFrEF patient (EF ≈ 34%, post-three-ablation,
on amiodarone) building a daily resonance-breathing habit as part of a
non-pharmacological vagal-training regimen. The clinical and behavioural
rationale is documented in `breathing-yoga-hfref.md`.

Existing mobile apps (Paced Breathing, iBreathe, Breathwrk) cover this
use case but require phone pickup and unlock. The user works at a Mac
terminal most of the day and wants a zero-friction, zero-distraction
tool that launches in under a second from an already-open iTerm window.

The product is a **habit scaffolding tool**, not a medical device. It
must make the right thing (a 6-bpm daily session) the easiest thing.

## 3. Scope

### In scope

- Slow paced-breathing timer at resonance frequencies (6 bpm / 5 bpm)
- Visual breath indicator in the terminal
- Optional audio cues at phase transitions
- Three named presets plus custom flags
- Pause / resume / quit controls during a session
- Session summary on exit (completed breaths, elapsed time, completion %)
- Safety information screen

### Out of scope (v1)

- Session logging to disk
- HRV measurement or integration
- Multi-user profiles
- Non-resonance breathing patterns (4-7-8, box, Wim Hof, etc.) — **deliberately excluded on safety grounds; see §5.4**
- Breath retention / kumbhaka — **deliberately excluded on safety grounds**
- Any rapid-breathing mode (kapalbhati, bhastrika) — **deliberately excluded**
- GUI, web UI, mobile support
- Internationalisation — English only
- Notifications, reminders, calendar integration

## 4. User profile and safety constraints

### Primary user

Single user (the author). Technical, consultant, runs tmux/iTerm all
day, expects CLI tools to Just Work. Cardiac profile summarised above.

### Safety constraints that shape the design

These are not optional features; they are load-bearing design
constraints that rule out whole categories of functionality.

**C1. No breath retention.** The app must never prompt for a hold phase.
Valid ratios are inhale:exhale only. If a user tries to pass a
three-number ratio (e.g. `4-7-8`), the app rejects with a clear error
referencing the safety rationale.

**C2. No rapid breathing.** The app must not allow total breath cycles
shorter than 8 seconds (i.e. >7.5 bpm). Hyperventilation-adjacent
patterns mobilise catecholamines — the opposite of the vagal intent.

**C3. Visible warning signs.** The safety screen (§6.5) lists the
specific stop-session symptoms from `breathing-yoga-hfref.md`:
lightheadedness, palpitations, tingling in hands or face.

**C4. Graceful interruption.** The session can be ended at any moment
by a single keypress or `Ctrl+C`. Exit must always succeed — no stuck
animation loops, no terminal left in a broken state.

**C5. Pre-session settle.** Every session begins with a 3-second
countdown during which the user can settle, close other apps, or abort
without having "missed" any breaths.

## 5. Functional requirements

### 5.1 Invocation

```console
$ breathe                         # auto-selects preset by time of day
$ breathe --preset morning        # named preset
$ breathe -d 20 -r 4-6            # custom
$ breathe --safety                # show safety info and exit
$ breathe --list-presets          # show presets and exit
$ breathe --quiet -d 5            # suppress startup warnings
$ breathe --help                  # standard argparse help
```

### 5.2 Presets

| Preset name | Duration | Ratio (inhale-exhale) | Target use |
|-------------|----------|-----------------------|------------|
| `morning`   | 10 min   | 5s-5s (6 bpm)         | Daily baseline, pre-email |
| `evening`   | 15 min   | 4s-6s (6 bpm, vagal)  | Sympathetic wind-down |
| `long`      | 20 min   | 4s-6s (6 bpm, vagal)  | Full dose, per Bernardi protocol |

Note: `evening` and `long` share the same 4-6 ratio intentionally —
`long` is the same vagal-emphasis pattern at a higher dose (20 min vs
15 min), matching the Bernardi protocol's recommended session length.

Presets are defined as a Python dict in the source file (§12), not
loaded from external config. v1 does not support user-defined presets.

### 5.3 Valid parameter ranges

| Parameter | Min | Max | Default | Validation error message |
|-----------|-----|-----|---------|--------------------------|
| Duration (minutes) | 1 | 60 | 10 | "Duration must be 1–60 minutes." |
| Inhale seconds | 3 | 10 | 5 | "Inhale must be 3–10 seconds." |
| Exhale seconds | 3 | 10 | 5 | "Exhale must be 3–10 seconds." |
| Total cycle (in + ex) | 8 | — | 10 | "Total breath cycle must be ≥ 8 seconds (no rapid breathing)." |

### 5.4 Rejected inputs (with explicit safety messaging)

| User input | Response |
|------------|----------|
| `--ratio 4-7-8` | Error: "Three-number ratios imply a breath hold. This app does not support breath retention. See `breathe --safety`." |
| `--ratio 2-2` | Error: "Total breath cycle must be ≥ 8 seconds (no rapid breathing)." |
| `--ratio foo` | Error: "Ratio must be in the form `inhale-exhale` (e.g. `5-5` or `4-6`)." |
| `--duration 0` | Error: "Duration must be 1–60 minutes." |
| `--duration 120` | Error: "Duration must be 1–60 minutes." |

### 5.5 Runtime controls (during a session)

| Key | Action |
|-----|--------|
| `space` | Pause / resume. Pause freezes the animation, mutes cues, and stops the session clock — paused time does not count toward elapsed duration or completion percentage. |
| `s` | Toggle sound on/off without pausing. |
| `q` or `Ctrl+C` | End session. Show exit summary. |

Keypresses are handled in raw-ish mode (`termios` `cbreak`) so the user
does not need to press Enter. If raw-mode setup fails (e.g. stdin is
not a TTY, as in a pipe or CI), the app falls back to running without
pause/quit keys and prints a one-line warning; `Ctrl+C` still works.

### 5.6 Exit summary

On session end (timer completes, `q` pressed, or `Ctrl+C`):

```console
Session summary
───────────────
Target:    10 min (morning preset, 5-5)
Completed: 7 min 42 s (77%)
Breaths:   46 full cycles
Status:    ended early (user)
```

A "full cycle" is one complete inhale followed by one complete exhale.
If the user exits mid-phase (during an inhale or partway through an
exhale), that incomplete cycle is not counted.

Completion percentage is `elapsed_breathing_time / target_duration`,
clamped to 100 %. Paused time is excluded from `elapsed_breathing_time`.

If the session completed naturally, the `Status` line reads `completed`.
If `Ctrl+C` was pressed or `q` was pressed, it reads `ended early (user)`.
If an unhandled exception ended it, the wrapper prints the traceback
*after* the summary.

## 6. Command-line interface

### 6.1 `breathe` (no args)

Auto-selects a preset based on the system clock at invocation:

| System time    | Auto-selected preset | Rationale |
|----------------|----------------------|-----------|
| 00:00 – 11:59  | `morning` (5-5, 10 min) | Equal ratio, moderate dose — energizing start |
| 12:00 – 16:59  | `long` (4-6, 20 min)    | Vagal emphasis, full Bernardi dose — afternoon recovery window |
| 17:00 – 23:59  | `evening` (4-6, 15 min) | Vagal emphasis, shorter — sympathetic wind-down before sleep |

Time is read from `time.localtime().tm_hour`. No timezone
configuration — uses whatever the OS reports.

`--preset NAME` or custom flags (`-d`, `-r`) override auto-selection.
Auto-selection only applies when no arguments are given.

When auto-selected, the header shows the preset name as usual
(e.g. `morning · 5-5 · ...`). No additional "auto" indicator is
needed — the user invoked with no args and knows why.

Rationale: the right breathing pattern depends on time of day. Making
the zero-argument default context-aware removes one more step from the
habit loop.

### 6.2 `breathe --preset NAME`

Runs the named preset. `NAME` is one of `morning`, `evening`, `long`.
Unknown preset names produce a helpful error listing the valid ones.

### 6.3 `breathe -d MINUTES -r RATIO`

Custom session. Both flags are optional independently. If only `-d` is
given, the default ratio `5-5` is used. If only `-r` is given, the
default duration `10` is used.

Long forms: `--duration`, `--ratio`. Standard argparse conventions.

### 6.4 `breathe --list-presets`

Prints the preset table from §5.2 and exits 0.

### 6.5 `breathe --safety`

Prints the following block verbatim and exits 0.

```text
Breathe CLI — safety notes
──────────────────────────

This app paces slow breathing at 6 breaths per minute for vagal tone
support. It is a habit tool, not a medical device.

STOP THE SESSION IMMEDIATELY if you experience:

  • Lightheadedness or dizziness — you may be breathing too deeply.
    Reduce depth, not rate. If it persists, stop.
  • Palpitations — stop, note the time, mention at your next
    cardiology visit.
  • Tingling in hands or face — hyperventilation signal. Stop,
    return to normal breathing.

This app deliberately does NOT support:
  • Breath retention (kumbhaka) of any length
  • Rapid breathing (kapalbhati, bhastrika, Wim Hof patterns)
  • Total breath cycles shorter than 8 seconds

Press q or Ctrl+C to end any session. Exit is always immediate.
```

### 6.6 `breathe --help`

Standard argparse help text. Include a one-line example under the
options block showing `breathe --preset morning`.

### 6.7 `breathe --version`

Prints `breathe 1.0` and exits 0.

## 7. Visual design

### 7.1 Layout

The session screen uses a fixed three-zone layout. Terminal width is
read via `shutil.get_terminal_size()` at session start; minimum
supported width is 40 columns. Below that, print a warning and run in
"minimal" mode (text-only, no centred visual).

```text
┌────────────────────────────────────────────────┐
│  morning · 5-5 · 02:37 / 10:00           [●]   │  ← header (1 line)
│                                                │
│                                                │
│                                                │
│                 INHALE                         │  ← phase label (1 line)
│                                                │
│         ████████████████░░░░░░░░░░░░░          │  ← breath bar (1 line)
│                                                │
│                                                │
│                                                │
│  space pause · s mute · q quit                 │  ← footer (1 line)
└────────────────────────────────────────────────┘
```

Vertical centring: compute once at session start using terminal height
(`shutil.get_terminal_size().lines`). Clear screen on start with
`\033[2J\033[H`, hide cursor with `\033[?25l`, restore on exit.

### 7.2 Header

Format: `{preset_or_custom} · {ratio} · {elapsed} / {total}   [{indicator}]`

- `preset_or_custom`: preset name, or literal string `custom` for `-d`/`-r`
- `ratio`: e.g. `5-5` or `4-6`
- `elapsed` / `total`: `MM:SS` format
- `indicator`: `●` when running, `⏸` when paused, `🔇` when muted, combined if both (e.g. `⏸ 🔇`)

### 7.3 Phase label

Centred horizontally. Either the literal string `INHALE` or `EXHALE`.
Uppercase, plain ASCII. Do not render it as ASCII-art or use a large
font — the user is looking at the breath bar, the label is just a
fallback anchor.

Colour: cyan (`\033[36m`) for INHALE, green (`\033[32m`) for EXHALE.
Reset with `\033[0m` after. If the terminal does not support colour
(`os.environ.get('NO_COLOR')` is set, or stdout is not a TTY), skip
escape codes entirely.

### 7.4 Breath bar

A horizontal bar 30 characters wide, centred. Filled portion uses the
Unicode full block `█` (U+2588), empty portion uses light shade `░`
(U+2591). On inhale, the bar fills left-to-right from 0 to 30 chars
over the inhale duration. On exhale, it empties right-to-left (i.e. the
filled portion shrinks from 30 to 0).

Update rate: 20 frames per second (50 ms sleep in the render loop).
That is smooth enough for a slow 5-second phase without stressing
older terminals.

If the terminal does not support Unicode box-drawing characters (detect
via `sys.stdout.encoding` not containing `utf`), fall back to `#` and `-`.

### 7.5 Footer

Plain text, dimmed (`\033[2m ... \033[0m`), single line, left-aligned
with 2-column indent. Shows the current key bindings. When paused,
change to `space resume · q quit`.

### 7.6 Rendering approach

Do not use `curses`. It is more than this app needs and has Mojave
edge cases with non-default terminals. Use direct ANSI escape codes:

- `\033[2J` — clear screen
- `\033[H` — cursor home (1,1)
- `\033[{row};{col}H` — cursor position
- `\033[K` — clear line from cursor
- `\033[?25l` / `\033[?25h` — hide / show cursor
- `\033[2m` / `\033[0m` — dim / reset
- `\033[36m` / `\033[32m` — cyan / green foreground

On every frame, move the cursor to each of the four zones and rewrite
them. Do not clear-and-redraw the whole screen each frame — it flickers
on Mojave's default Terminal.app.

### 7.7 Terminal restoration on exit

Wrap the session in `try` / `finally`. In `finally`:

- Restore cursor visibility (`\033[?25h`)
- Reset colours (`\033[0m`)
- Restore termios settings to the state captured before `cbreak`
- Move cursor to a line below the visual and print the exit summary

This must run on `Ctrl+C`, normal completion, and any exception.

## 8. Audio design

### 8.1 Mechanism

The primary audio backend is `AudioServicesPlaySystemSound` from the
AudioToolbox C framework, called via `ctypes` (stdlib). At startup,
both sound files are registered with `AudioServicesCreateSystemSoundID`.
Playback is a single C function call with near-zero latency — no
NSRunLoop needed, no subprocess spawn.

```python
# Simplified — see _SystemSoundPlayer in breathe.py for full ctypes setup
sound_id = register_sound(path)                    # once at startup
AudioServicesPlaySystemSound(sound_id)             # per transition, ~0 ms
```

Sound playback is asynchronous and must never block the render loop.

**Why not NSSound?** `NSSound.play()` dispatches through the
`NSRunLoop`, which is never serviced in a CLI app. Sounds either
don't play at all, or play with unpredictable latency.

**Why not afplay?** `subprocess.Popen` incurs ~100–200 ms of
process-spawn latency per sound, causing audible desync.

### 8.2 Sound files

Use macOS built-in system sounds in `/System/Library/Sounds/`:

| Phase transition | Sound file | Reason |
|------------------|------------|--------|
| Start of inhale  | `Tink.aiff` | Short, crisp, upward-perceived |
| Start of exhale  | `Pop.aiff`  | Short, softer, downward-perceived |

Volume follows the system alert volume setting (System Preferences >
Sound > Alert volume). `AudioServicesPlaySystemSound` does not support
per-sound volume control. This is an acceptable tradeoff for the
latency gain; the user sets their alert volume once.

### 8.3 Fallback chain

The audio subsystem tries backends in order:

1. **AudioToolbox** (`AudioServicesPlaySystemSound` via ctypes) —
   near-zero latency, no run loop dependency, pre-registered sound IDs.
   Used on all standard macOS installs.
2. **afplay** (`subprocess.Popen`) — higher latency (~100–200 ms per
   sound due to process spawn), but still functional. Used if the
   AudioToolbox ctypes setup fails for any reason.
3. **Terminal bell** (`\a` / `\x07`) — used if `afplay` is missing or
   sound files are absent. A single warning is printed at startup
   (`audio unavailable: falling back to terminal bell`).
4. **Silent** — if the terminal bell is also disabled, audio degrades
   to none. The session runs normally in all cases.

### 8.4 Muting

Default: audio on. Runtime toggle: `s`. CLI flag: `--no-sound` (alias
`-n`) disables audio for the whole session.

### 8.5 Quiet mode

CLI flag: `--quiet` (alias `-q`). Suppresses all non-error informational
messages at startup (audio fallback warnings, narrow-terminal warnings).
Does not affect the session display, exit summary, or error messages.
Useful when the user already knows about a degraded environment and does
not want to see the same warning every session.

Note: the `-q` short flag does not conflict with the `q` runtime key,
which is only active during a session and is read from stdin, not argv.

## 9. Architecture and file layout

### 9.1 File layout

```text
breathe.py          ← single file, executable with shebang
```

That is the entire deliverable. No `requirements.txt`, no `setup.py`,
no directory structure. If the implementer feels the urge to split
this into modules, resist it — the whole thing fits in under 500 lines
and the user will read the source to audit it.

### 9.2 Module structure within `breathe.py`

Top-to-bottom:

1. Shebang `#!/usr/bin/env python3`
2. Module docstring with one-line description and author
3. Imports (stdlib only: `argparse`, `os`, `sys`, `time`, `shutil`, `signal`, `subprocess`, `termios`, `tty`, `select`, `dataclasses`)
4. Constants: `VERSION`, `PRESETS` dict, sound paths, ANSI codes, safety text
5. `@dataclass` classes: `SessionConfig`, `SessionState`
6. Utility functions: `play_sound`, `supports_colour`, `supports_unicode`, `format_time`, `get_terminal_size`
7. Rendering functions: `clear_screen`, `draw_header`, `draw_phase`, `draw_bar`, `draw_footer`, `render_frame`
8. Input handling: `setup_raw_tty`, `restore_tty`, `poll_key`
9. Core loop: `run_session(config)` → `SessionState`
10. CLI handlers: `print_safety`, `print_presets`, `parse_ratio`, `build_config`
11. `main()` with argparse wiring
12. `if __name__ == '__main__': main()`

### 9.3 Core loop pseudocode

```text
run_session(config):
    setup terminal (raw mode, hide cursor)
    try:
        clear screen, draw static header
        do 3-second countdown
        mark session_start = time.monotonic()
        next_boundary = session_start   # ideal wall-clock phase edge
        total_paused = 0
        while elapsed_breathing < config.duration_seconds:
            for phase in (INHALE, EXHALE):
                phase_duration = config.inhale_s if INHALE else config.exhale_s
                phase_end = next_boundary + phase_duration
                play sound for phase
                while time.monotonic() < phase_end:
                    key = poll_key()  # non-blocking
                    handle key (pause / mute / quit)
                    if paused:
                        pause_start = time.monotonic()
                        wait on key, then resume
                        pause_dur = time.monotonic() - pause_start
                        total_paused += pause_dur
                        next_boundary += pause_dur  # shift ideal edge
                        phase_end    += pause_dur
                    if quit: raise SessionAborted
                    progress = (now - next_boundary) / phase_duration
                    render_frame(state, phase, progress)
                    sleep 50 ms
                next_boundary = phase_end  # advance to ideal edge
                # phase complete — count only after EXHALE (= one full cycle)
                if phase is EXHALE:
                    increment breath counter
            elapsed_breathing = time.monotonic() - session_start - total_paused
            if elapsed_breathing >= duration_seconds: break
    finally:
        restore terminal
    return state
```

**Timing model.** Phase boundaries are computed from ideal offsets
anchored to `session_start`, not from `time.monotonic()` at the moment
the previous phase finishes. Each frame's `time.sleep(50 ms)` overshoots
by 1–3 ms due to work before and after the sleep; without anchored
boundaries this accumulates to seconds of audible drift over a full
session. The `next_boundary` variable eliminates drift by advancing by
the exact phase duration at each transition.

### 9.4 Key handling detail

Non-blocking stdin read using `select.select([sys.stdin], [], [], 0)`
with a zero timeout. In `cbreak` mode, a single byte is returned per
keypress for printable keys; `Ctrl+C` triggers `KeyboardInterrupt` as
normal because `cbreak` preserves signal processing (unlike full raw
mode).

This pattern works correctly under tmux and screen, which is relevant
because the primary user runs tmux daily. The pty layer that tmux
interposes between the shell and the real terminal preserves `cbreak`
semantics and `select.select` readability on the stdin fd.

Map bytes: `b' '` → pause, `b's'` → mute toggle, `b'q'` → quit. Ignore
other bytes.

### 9.5 Signal handling

Install a `SIGINT` handler that sets an abort flag and lets the main
loop exit cleanly rather than letting the default `KeyboardInterrupt`
propagate mid-render (which can leave the terminal in a bad state).
The `finally` block in `run_session` handles restoration regardless.

## 10. Error handling and edge cases

| Condition | Behaviour |
|-----------|-----------|
| Python version < 3.7 | Print `requires Python 3.7+` and exit 1 before any other logic |
| Not a TTY (piped output) | Warn and run without pause/quit keys, no animation — just sleep for the session, print summary at end |
| Terminal < 40 cols wide | Warn and run in minimal mode (phase label + bar only, no centring) |
| `afplay` missing | Warn once, fall back to terminal bell |
| Sound file missing | Warn once, fall back to terminal bell |
| Unicode not supported | Use `#`/`-` for the bar, `INHALE`/`EXHALE` text is already ASCII |
| Ratio total < 8 s | Reject at parse time with safety-framed error (§5.4) |
| Ratio has 3 components | Reject at parse time with safety-framed error (§5.4) |
| `Ctrl+C` mid-session | Restore terminal, print summary with status `ended early (user)`, exit 0 |
| Unhandled exception | Restore terminal, print summary, then print traceback, exit 1 |
| Terminal resize mid-session | Ignore in v1 — layout computed once at start. Document as known issue. |

## 11. Non-functional requirements

- **Startup time**: under 200 ms from shell to first frame (excluding the 3-second settle countdown). Stdlib-only + no I/O makes this trivial.
- **Dependencies**: none beyond Python 3.7 stdlib. No `pip install` step.
- **Portability**: macOS only (uses `afplay`). Document this in the top docstring. Do not bother with Linux/Windows fallbacks in v1.
- **Code size**: target under 500 lines of Python including docstrings. Cap at 700.
- **Auditability**: the user will read the source. Favour clarity over cleverness. Type hints on public function signatures.
- **Exit cleanliness**: the terminal must be left in a usable state after any exit path, including unhandled exceptions. This is tested explicitly (§13).

## 12. Concrete constants

Commit these values directly into the source file. Do not invent a
config-file layer.

```python
VERSION = '1.2'

PRESETS = {
    'morning': {'duration_min': 10, 'inhale_s': 5, 'exhale_s': 5},
    'evening': {'duration_min': 15, 'inhale_s': 4, 'exhale_s': 6},
    'long':    {'duration_min': 20, 'inhale_s': 4, 'exhale_s': 6},
}

SOUND_INHALE = '/System/Library/Sounds/Tink.aiff'
SOUND_EXHALE = '/System/Library/Sounds/Pop.aiff'
AFPLAY       = '/usr/bin/afplay'
AFPLAY_VOL   = '0.3'

BAR_WIDTH       = 30
FRAME_RATE_HZ   = 20
COUNTDOWN_SECS  = 3
MIN_TERM_WIDTH  = 40
MIN_CYCLE_SECS  = 8

ANSI_CLEAR     = '\033[2J\033[H'
ANSI_HOME      = '\033[H'
ANSI_HIDE_CUR  = '\033[?25l'
ANSI_SHOW_CUR  = '\033[?25h'
ANSI_RESET     = '\033[0m'
ANSI_DIM       = '\033[2m'
ANSI_CYAN      = '\033[36m'
ANSI_GREEN     = '\033[32m'
```

## 13. Acceptance criteria

Implement these as a short self-test that the implementer runs
manually; no test framework required.

### 13.1 Smoke tests

1. `breathe --help` prints help and exits 0.
2. `breathe --version` prints `breathe 1.2` and exits 0.
3. `breathe --safety` prints the safety block and exits 0.
4. `breathe --list-presets` prints the preset table and exits 0.
5. `breathe -d 1` runs for ~60 seconds, renders breath animation, exits cleanly with `completed` status.
6. `breathe --preset morning` starts a 10-minute 5-5 session. `Ctrl+C` during the first minute exits within 1 second and the terminal is fully usable (prompt returns on its own line, cursor visible, no leftover colour).

### 13.2 Safety-rejection tests

7. `breathe -r 4-7-8` exits non-zero with the three-number ratio error message.
8. `breathe -r 2-2` exits non-zero with the "cycle must be ≥ 8 seconds" error.
9. `breathe -d 0` exits non-zero with the duration-range error.
10. `breathe -d 120` exits non-zero with the duration-range error.

### 13.3 Degradation tests

11. With `NO_COLOR=1 breathe -d 1`, the session renders without ANSI colour and still completes.
12. `breathe -d 1 | cat` (non-TTY stdout) prints a warning, runs for 60 seconds, and prints a summary — without an animated frame loop.
13. Rename `/usr/bin/afplay` temporarily (or `chmod -x`), run `breathe -d 1`: startup warns about audio fallback, session runs, bell is heard at phase transitions.
14. Repeat test 13 with `breathe --quiet -d 1`: no startup warning is printed, session runs normally with bell fallback.

### 13.4 Runtime-control tests

15. During a session, pressing `space` freezes the bar and header shows `⏸`. Pressing `space` again resumes. Paused time is excluded from the elapsed clock — if you pause for 30 seconds during a 1-minute session, the session should take ~90 seconds wall-clock to complete.
16. During a session, pressing `s` toggles the mute indicator `🔇` and stops/restores sound without pausing.
17. During a session, pressing `q` exits with `ended early (user)` status within 1 second.

### 13.5 Terminal-restoration test

18. Inject a deliberate `raise RuntimeError('boom')` inside the render loop. Run the app. Confirm: summary prints, then traceback, then prompt returns on its own line with cursor visible and no lingering colour codes.

### 13.6 Time-of-day default test

19. Run `breathe` with no arguments at different times of day (or mock `time.localtime`). Verify:
    - Before noon: header shows `morning · 5-5 · ... / 10:00`
    - 12:00–16:59: header shows `long · 4-6 · ... / 20:00`
    - 17:00+: header shows `evening · 4-6 · ... / 15:00`

## 14. Build and run

### 14.1 Install

```bash
# 1. Save breathe.py somewhere on PATH (e.g. ~/bin)
mv breathe.py ~/bin/breathe
chmod +x ~/bin/breathe

# 2. Verify Python 3.7+ is available
python3 --version   # should be ≥ 3.7.0

# 3. Run
breathe --safety
breathe --preset morning
```

### 14.2 Uninstall

```bash
rm ~/bin/breathe
```

No dotfiles, no caches, no state. That is the point.

## 15. Implementation notes for Claude Opus 4.6

Three things the implementer should double-check before calling it done:

- **The terminal-restoration path.** Every exit — normal, `Ctrl+C`, exception, `q` — must pass through the same `finally` that restores termios, shows the cursor, and resets colours. Write this first, before anything else, and verify it with test 17.
- **The non-blocking keypoll.** `select.select` with a zero timeout on stdin inside `cbreak` mode is the right pattern on macOS. Do not use `curses.getch` or `threading.Thread` — both add failure modes that are not worth it for four keys.
- **The audio fallback.** Do not hard-fail if `afplay` is missing or a sound file is absent. Warn once, degrade to `\a`, continue. The user's habit is more important than the cue.

Do not add features not listed here. If an ambiguity blocks progress,
stop and ask rather than guessing — especially around the safety
constraints in §4 and §5.4. Anything that could be interpreted as
breath retention or rapid breathing is out of scope by design, not by
omission.
