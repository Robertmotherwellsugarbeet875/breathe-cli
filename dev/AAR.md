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

## 2026-05-30 — Bug fix round (#6, #10, #12), audio refactor, spec slimdown (v1.6)

**What went well:**
- Bug investigation was efficient — read the code, identified root causes from structure (stale frame on `continue`, `int()` truncation, missing final render), fixed with minimal changes
- Sound debugging was systematic — tested both audio backends independently, quickly isolated AudioToolbox as the silent failure, swapped priority
- Refactoring removed 65 lines (711→646) by dropping dead code (AudioToolbox) rather than cosmetic compaction — the right kind of line reduction
- Spec slimdown was overdue and landed well — 785→108 lines, keeping only the load-bearing parts (safety constraints, acceptance tests)

**What didn't go well:**
- Didn't flag the spec's post-hoc drift proactively — the user had to ask "what's the value of keeping this?" before I surfaced it
- After slimming the spec, missed stale cross-references in CLAUDE.md until explicitly asked to check other documents

**What we'll do differently:**
- After any structural change, proactively scan all docs for stale references and coordination issues
- When a document is being maintained post-hoc rather than driving work, flag that to the user as a potential simplification opportunity

## 2026-05-30 — Bug #13 fix, automated test suite (v1.7)

**What went well:**
- Debug logging to a file was the breakthrough — after four failed attempts based on code reading, instrumenting the actual runtime exposed the root cause in minutes
- The fix was simple and correct once the real problem was identified: two lines at config time to round `duration_s` up to a whole number of cycles
- Test suite infrastructure (42 tests) now exists, covering all logic and arithmetic paths including the bug #13 fix

**What didn't go well:**
- Spent five fix attempts patching symptoms (display rounding, phase offsets, stepped countdown) without questioning whether the inputs to the loop were correct — classic fixation on the wrong abstraction level
- Failed to ship tests alongside the fix — user had to remind me, which is a basic engineering discipline failure
- The `replace_all` for `session_s` clobbered unrelated `session_start_time` variables — careless use of a blunt tool

**What we'll do differently:**
- When designing flags or parameters that interact, always validate logical consistency at config time — the `-d`/`-r` inconsistency was introduced at the design level and haunted us for several rounds of failed fixes. Inputs that must be coordinated should be coordinated before they reach the runtime loop
- When a bug survives multiple fix attempts, stop and instrument — add debug logging and observe actual values instead of reasoning from code alone
- Always ship tests with code changes, never as a follow-up
- When using replace_all, grep for collateral matches first

## 2026-05-30 — Science, functional presets, safety, publishing (v1.8)

**What went well:**
- Literature review was thorough — verified all 6 DOIs against PubMed before adding citations, caught that the README was attributing the O2 sat claim to the wrong Bernardi paper (2002 instead of 1998)
- Preset rename (morning→balanced, evening→calm, long→extended) was clean — replace_all across files with no collateral damage, all 44 tests passed immediately
- The exhale ratio cap (≤2x inhale) emerged naturally from reviewing the science — a safety constraint grounded in evidence, not speculation
- Resonance frequency measurement protocol is concrete and actionable — specific hardware, step-by-step procedure, exact commands

**What didn't go well:**
- Hit 701 lines with the disclaimer and had to trim — the 700-line cap is now fully consumed with zero margin
- Didn't anticipate that `gh repo create` would fail on an existing `origin` remote — minor, but added a manual step

**What we'll do differently:**
- Before adding any feature, check available line budget first and flag if it requires trimming
- When creating a new GitHub repo from an existing local repo, check the current remote setup before running `gh repo create`

## 2026-05-30 — Social card, repo description, Medium draft

**What went well:**
- Caught the `sharp`/Mojave crash diagnosis quickly — identified the `_aligned_alloc` symbol as a macOS 10.15+ dependency, avoided image processing paths for the rest of the session
- Social card workflow was efficient — resize + crop with ImageMagick guided by vision, imgcrush for compression, all in a few steps
- Caught the `_config.yml` description mistake in time — short tagline is right for repo description but wrong for Pages SEO meta

**What didn't go well:**
- Deleted `social-card.png` before the user was done with it — had to re-export from HTML. Should have asked before cleaning up an asset that wasn't committed
- Changed the Jekyll description without thinking through the different purposes of repo description vs. Pages meta description — user had to catch this
- Previous session crashed (dyld/sharp incompatibility on Mojave) and all conversation context was lost. Important decisions and state that existed only in context disappeared with it

**What we'll do differently:**
- Don't delete untracked assets until the user confirms they're fully done with them — "clean up" should mean "remove what's confirmed unnecessary," not "remove all untracked files"
- When the same text (description, title) appears in multiple places, consider whether each instance serves a different audience before making them identical
- Treat context as perishable: commit work frequently, update NEXT-SESSION.md and TODO.md as decisions are made (not just at session close), and write important state to files immediately rather than holding it in conversation
