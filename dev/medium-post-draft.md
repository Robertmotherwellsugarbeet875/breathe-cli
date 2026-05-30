# The Market of One: How AI Lets Domain Experts Build the Software Only They Would Build

*Applying Goldratt's Six Questions to AI-assisted development*

---

I'm a cardiology patient with heart failure. One of the few things I can do for myself — besides taking the pills — is breathe slowly. Resonance breathing at about 6 breaths per minute strengthens vagal tone, and the clinical evidence for it in heart failure patients is solid (Bernardi et al. 1998, 2002).

There are breathing apps. Hundreds of them. None of them are right. They add breath holds (dangerous for cardiac patients — Valsalva-like pressure can trigger syncope or arrhythmia). They add rapid breathing patterns (the opposite of vagal training). They wrap everything in subscription paywalls and meditation aesthetics. They require an iPhone.

What I needed was simple: a pacer in the terminal that does exactly one thing, refuses to do anything unsafe, and runs on the Mac I already have open. No installs, no accounts, no dependencies. So I built it — with AI.

The result is [Breathe CLI](https://github.com/marekkowalczyk/breathe-cli): a single Python file, 700 lines, no dependencies, MIT licensed. It took a few sessions of working with Claude to go from idea to published app with Homebrew tap, PyPI package, clinical citations, and a 42-test automated suite. I am not a professional software developer.

This is not a story about AI writing code. It's a story about what happens when the cost of building software drops to near zero for a person who knows exactly what they need.

## Goldratt's lens

Eliyahu Goldratt — the Theory of Constraints thinker — left us a framework for evaluating any new technology: six questions that cut through hype and force you to identify whether a technology actually removes a real limitation, or just creates a solution looking for a problem.

I've found this framework useful for thinking about what AI coding assistants actually change. Not in the abstract, but concretely — what limitation did they remove for me, and what had to change for that to matter?

### 1. What is the power of the technology?

An AI coding assistant (in my case, Claude in the terminal) can write, debug, test, and refactor code through conversation. You describe what you want in natural language, it produces working code. It knows languages, frameworks, libraries, conventions. It can hold a spec in context, enforce constraints across a session, and catch its own mistakes when you point them out.

What it cannot do: it cannot know what you need. It cannot decide that breath retention is dangerous for cardiac patients. It cannot feel the difference between a breathing app that's merely functional and one that's safe to use when your heart doesn't work properly. It cannot set priorities.

### 2. What limitation does it eliminate?

Here is the core: **building quality software has historically required either a team or years of solo craft.** If you're a domain expert — a doctor, a patient, a researcher, a teacher — and you see a gap that no commercial product fills, you're stuck. You can file a feature request and hope. You can hire a developer and pay. You can learn to code over months and years. Or you can give up and adapt to tools that don't quite fit.

AI eliminates this limitation. Not partially — almost entirely. A person who understands their problem deeply, can think clearly about requirements, and can evaluate whether a solution is correct can now build production-quality software in days. The bottleneck was never the idea or the domain knowledge. It was the translation layer — turning intent into working code.

### 3. What workarounds exist today?

Before AI coding assistants, domain experts coped in familiar ways:

- **Adapt to what exists.** Use a meditation app that sort of does breathing, ignore the features that don't apply, tolerate the ones that are actively wrong.
- **Use spreadsheets and scripts.** Cobble together something functional but fragile — a timer in a shell script, a macro in Excel. It works for you but isn't shareable.
- **Hire someone.** Commission a developer to build what you need. Expensive, slow, and you spend most of the budget explaining the domain rather than building.
- **File feature requests.** Ask the vendor to add what you need. It goes into a backlog. Your market is too small to prioritize.
- **Go without.** Accept that the tool you need doesn't exist and won't.

These workarounds share a common shape: the domain expert compromises because the cost of building is too high relative to the market size. A breathing app for cardiac patients who use the terminal is not a viable product. No one would fund it. No one would staff it. The market is maybe a few hundred people. Maybe fewer.

### 4. What rules need to change?

This is where it gets interesting. If building software is now cheap for domain experts, several assumptions collapse:

**"Software worth building has to serve a large market."** No. If the cost of building is near zero, the threshold for "worth building" drops to a market of one — yourself. Anything you publish beyond that is a gift.

**"Users should not build their own tools."** This is an old rule from when building was hard and fragile. If an AI can enforce code quality, write tests, maintain consistency, and catch regressions, the output of a domain-expert-plus-AI collaboration can be as good as — sometimes better than — what a team of generalists produces. Better, because the person specifying the requirements actually lives with the problem.

**"Domain experts need to learn to code first."** Not exactly. They need to learn to think precisely about requirements, edge cases, and failure modes. They need to evaluate output critically. These are skills, but they're different skills than writing Python from scratch. A cardiology patient who understands Valsalva physiology, reads the Bernardi papers, and can articulate exactly why breath holds are dangerous doesn't need to know how `select.select` works. They need to know what their app must never do.

### 5. What should the technology do to avoid resistance?

Goldratt's fifth question, in Schragenheim's later formulation, is about designing the application of the technology so that adoption doesn't create new problems or trigger resistance.

For AI coding assistants, the resistance is real and comes from two directions:

**From developers:** "AI will take our jobs." This framing misses the point. AI-assisted domain experts aren't competing with professional developers. They're building things that would never have been built at all — the long tail of software that no company would fund because the market is too small. A cardiac patient's breathing pacer isn't taking work from anyone. It's creating something from nothing.

**From users of the resulting software:** "Can I trust code written by AI?" This is a legitimate concern, and the answer has to be: look at the code. The entire point of single-file, no-dependency, MIT-licensed software is that you can read every line. The safety constraints are in the source. The clinical citations are checkable. The tests are runnable. Trust is earned through transparency, not authority — and this is easier, not harder, when the codebase is 700 lines instead of 70,000.

### 6. How to build, capitalize, and sustain?

Goldratt's sixth question is about strategy: how to capture and extend the value. For a market-of-one app, the strategy is simple and inverted:

**Build:** Solve your own problem first. Don't speculate about what others might need. If you have a condition, you are the spec.

**Capitalize:** Publish openly. MIT license, public repo, package managers (pip, Homebrew). The "customer acquisition cost" is zero because you're not selling anything. If someone with the same condition finds it useful, the investment has paid for itself.

**Sustain:** Keep the scope small. A single-file app with no dependencies has near-zero maintenance burden. There's no infrastructure to rot, no subscription to expire, no team to coordinate. It stays useful as long as Python runs.

## The deeper point

Goldratt's framework reveals something that the usual AI discourse misses. The question isn't whether AI can write code (it can). The question is: **what limitation does that remove, and for whom?**

For professional developers, AI removes some friction — autocomplete on steroids, faster boilerplate, quicker prototyping. Useful, but incremental. The fundamental limitation (knowing how to build software) wasn't their bottleneck.

For domain experts, AI removes the *entire barrier*. The person who understands the problem best can now build the solution. No translation layer, no intermediaries, no compromises forced by misaligned incentives or insufficient market size.

The result is a new category of software that couldn't exist before: tools built by one person, for one person, shared freely in case anyone else in the same situation might benefit. The market of one, scaled to the long tail of human need.

My heart doesn't work very well. But I can open a terminal and breathe slowly for fifteen minutes, paced by an app that refuses to let me do anything that might make things worse. That app exists because the cost of building it fell below the threshold of one person's motivation.

That's what the technology does. Not the code. The permission to build.

---

*[Breathe CLI](https://github.com/marekkowalczyk/breathe-cli) is free, open source, and available via `pip install breathe-cli` or `brew tap marekkowalczyk/breathe && brew install breathe`. It is not a medical device.*

*The six questions framework comes from Goldratt, Schragenheim, and Ptak's* Necessary But Not Sufficient *(2000), with refinements by Schragenheim in the TOCICO Body of Knowledge (2019).*
