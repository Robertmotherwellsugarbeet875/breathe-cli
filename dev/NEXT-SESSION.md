# Next Session

v1.9 shipped (GitHub release + PyPI). Added Windows 11 support (community PR #3) and updated pyproject.toml classifiers. Currently 700 lines (at the hard cap).

Writing files (blog post, LinkedIn draft, Medium draft, PUBLISH.taskpaper) moved to `~/repos/writing`.

## Open items

- **Windows test coverage** — `test_breathe.py` has no tests for Windows-specific code paths (winsound selection, msvcrt key polling, console setup). Low priority since these are platform-gated and hard to test on macOS.
- **Triage HN feature requests** — breath holds/4-7-8 (TODO #14), biofeedback-triggered cues, pomodoro. Decide which are in scope. #14 is already tracked but needs a design decision on safety architecture.
- **Session progress bar — cycle count** (TODO #8), **Personal resonance frequency** (TODO #15) — both need line trimming first; file is at the 700-line cap.
