# After Action Review

Continuous improvement log. Each session ends with a brief review: what went well, what didn't, what to change. This is the POOGI (Process Of Ongoing Improvement) record for this project.

## 2026-05-15 — Add session logging and TODO items

**What went well:**
- Spec-first workflow worked smoothly again — caught the out-of-scope constraint before writing code, amended the spec cleanly, then implemented from it
- Implementation was straightforward and fit within the 700-line cap (exactly 700)
- Testing confirmed logging works correctly in both normal and `--no-log` paths

**What didn't go well:**
- The 700-line hard cap required significant time spent on cosmetic line-count trimming (collapsing blank lines, compacting docstrings, extracting `_die()` helper). The feature itself was ~30 lines but fitting it required touching 15+ unrelated spots
- TODO.md had accumulated structural issues (duplicate `## Bugs` headers, item #2 not marked done) — should have been caught at the end of the previous session

**What we'll do differently:**
- When approaching the 700-line cap, consider whether the cap should be revisited in the spec rather than spending effort on cosmetic compaction. The file is already well past the 500-line target
- Always clean up TODO.md during the close checklist, not just when adding items

## 2026-05-26 — Go rewrite analysis + countdown timer (v1.4)

**What went well:**
- Six Thinking Hats analysis was a good lightweight way to evaluate a rewrite idea without wasting implementation effort — concluded "not worth it" with clear reasoning
- Spec-first workflow continues to work well: amended spec to v1.4 before touching code
- The countdown change was surgically small (one line of logic) and required no new architecture
- Caught the 701-line cap violation immediately and fixed by inlining the computation

**What didn't go well:**
- Hit the 700-line cap on a trivial +1 line change — the cap is now fully consumed and any future feature will face the same friction

**What we'll do differently:**
- Nothing process-wise — this session was clean. The line cap issue is a known constraint already tracked in TODO and prior AAR

## 2026-05-26 — State machine refactor, pause-resume reset (v1.5)

**What went well:**
- Visual testing workflow — asking user to run and inspect the TUI was far more effective than scripting pty captures, which wasted time and tokens
- The state machine refactor landed clean: net -5 lines, simpler mental model, and the pause-resume behavior works correctly
- Iterative design through conversation: the elapsed time model evolved through three rounds of feedback (wall-clock minus pauses → completed breathing time → smooth countdown with snap-back) and each round sharpened the design

**What didn't go well:**
- First attempt at pause-resume (flag-based break out of nested loops) caused a 4-second overshoot bug and had to be fully reverted — should have recognized the nested loop structure was the root problem earlier instead of trying to patch it
- Spent significant tokens on programmatic pty capture that produced no useful output — the app needs a real terminal

**What we'll do differently:**
- For TUI changes, always ask the user to run and visually verify — never attempt programmatic terminal capture (already saved to memory)
- When a feature requires breaking out of multiple loop levels with flags, treat that as a design smell and consider restructuring first
