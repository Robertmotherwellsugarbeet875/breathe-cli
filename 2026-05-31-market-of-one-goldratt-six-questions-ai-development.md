---
title: "The Market of One"
subtitle: "When building software costs less than needing it"
subject: "AI-assisted software development by domain experts"
keywords: "Market of One, AI-assisted development, Claude Code, Goldratt's Six Questions, Theory of Constraints, domain experts, niche software, Breathe CLI, software democratization, excavator problem, discovery gap"
abstract: |
  When AI coding assistants drop the cost of building software to near zero, the economic threshold for "worth building" drops to a single user. This article argues that domain experts — people who understand a problem deeply but cannot code — can now build production-quality tools for their own hyper-specific needs. The author, a cardiac patient, built a terminal-based breathing pacer (Breathe CLI) with Claude Code in hours rather than months. Using Goldratt's Six Questions framework, the piece evaluates the power, limitations, adoption barriers, and strategy of this "Market of One" pattern, introduces "the excavator problem" (AI faithfully executes design-level human errors), and identifies the next systemic bottleneck: discovering hyper-niche software organized by human situation rather than technical category.
documentclass: article
lang: en
author: "Marek Kowalczyk"
date: 2026-05-31
stamp: true
draft: true
# --- Structured summary for AI ingestion ---
document:
  type: thought-leadership article
  scope: "Evaluates AI-assisted development as a paradigm shift for domain experts, using personal case study and Goldratt's Six Questions"
  audience: "Domain experts with deep knowledge and specific unsolved problems; secondary audience: TOC practitioners, AI practitioners, Medium readers"
  target_publication: Medium
  word_count_approx: 3200
author_context:
  name: "Marek Kowalczyk"
  orcid: "https://orcid.org/0009-0008-3874-6736"
  roles: [Theory of Constraints consultant, adjunct professor, cardiac patient]
  location: "Warsaw, Poland"
  relevance: "Author is both the domain expert and the case study subject — a non-developer who built production software with AI"
core_framework:
  name: "Goldratt's Six Questions"
  origin: "Necessary But Not Sufficient (2000), Goldratt, Schragenheim, Ptak; refined by Schragenheim via TOCICO"
  application: "Systematic evaluation of AI-assisted development: power, limitation eliminated, workarounds, rule changes, resistance design, strategy"
case_study:
  name: "Breathe CLI"
  repository: "https://github.com/marekkowalczyk/breathe-cli"
  purpose: "Terminal-based resonance breathing pacer (6 breaths/min) for cardiac patients; omits dangerous patterns (Valsalva-like pressure)"
  stack: "Python, single-file, 700 lines, no dependencies, MIT license"
  distribution: "PyPI (pip install breathe-cli), Homebrew tap"
  quality: "44-test automated suite, clinical citations embedded"
  economics:
    traditional_estimate: "170–220 hours, $12,000–$40,000, 3–4 months"
    ai_assisted_actual: "5–10 hours, negligible cost"
key_concepts:
  - name: "Market of One"
    definition: "Software built by a domain expert to solve their own problem, where the market is too small to justify traditional development"
  - name: "The excavator problem"
    definition: "AI multiplies human capability but faithfully executes human errors, demanding advanced verification from the operator"
  - name: "The discovery gap"
    definition: "Hyper-niche tools cannot be found because platforms index by technical category, not by the human situation that motivated the code"
structural_sections:
  - "Introduction (personal story, problem, Breathe CLI)"
  - "Is this for you? (domain expert profile, anti-profile, requirement-thinking)"
  - "The hard questions (Goldratt Q1–Q6: power, limitation, workarounds, rules, resistance, strategy)"
  - "The next bottleneck (discovery gap)"
  - "Conclusion (personal resolution, agency, medical disclaimer)"
references_mentioned:
  - "Bernardi et al. — resonance breathing and vagal tone research"
  - "Goldratt, Schragenheim, Ptak — Necessary But Not Sufficient (2000)"
  - "Schragenheim — Six Questions refinements (TOCICO)"
  - "David Skoll — Remind (1992), early market-of-one precedent"
  - "Anthropic — Claude Code (AI coding agent)"
---

I'm a cardiology patient with heart failure. One of the few things I can do for myself — besides taking the pills — is breathe slowly. Resonance breathing at about six breaths per minute strengthens vagal tone — a claim backed by two decades of cardiology research. (The evidence base is smaller than for pharmaceuticals, for the obvious economic reasons.)

There are breathing apps. Hundreds of them. None of them are right. They add breath holds (dangerous for cardiac patients — Valsalva-like pressure can trigger syncope or arrhythmia). They add rapid breathing patterns (the opposite of vagal training). They wrap everything in subscription paywalls and meditation aesthetics. They require an iPhone.

What I needed was simple: a pacer in the terminal that does exactly one thing, refuses to do anything unsafe, and runs on the Mac I already have open. No installs, no accounts, no dependencies. So I built it — with Claude Code, Anthropic's AI coding agent in the terminal.

The collaboration went deeper than writing code. Claude Code researched the clinical literature under my guidance, verifying the Bernardi studies and identifying contraindicated breathing patterns. I brought the lived experience and the clinical questions; Claude Code brought the research capacity and the engineering.

The result is [Breathe CLI](https://github.com/marekkowalczyk/breathe-cli): a single Python file, 700 lines, no dependencies, MIT licensed. It took a few sessions to go from idea to published app with Homebrew tap, PyPI package, clinical citations, and a 44-test automated suite.

This is not a story about AI writing code. It's a story about what happens when the cost of building software drops to near zero for a person who knows exactly what they need.

## Is this for you?

The obvious objection is "I'm not a coder." That's exactly the point. The question isn't whether you can code — it's whether you can think clearly about what you need.

**The person this pattern works for** has a few specific traits. They have deep knowledge in a domain — not casual familiarity, but years of lived or professional experience. They have a specific, well-defined problem, not a vague wish. They can articulate what the tool must do and — critically — what it must never do. They can look at a result and say "this is wrong" with reasons, even if they couldn't have produced the result themselves. They have patience for iterative conversation: describing, evaluating, correcting, describing again. And they have some baseline comfort with technical tools — not necessarily a terminal, but enough to not panic at a command line or a configuration file.

I fit this profile not because I'm technical (I'm not a developer), but because I've spent thirty years consulting on complex systems, which means I think in terms of requirements, constraints, and failure modes. That's the skill that transfers. Not coding — thinking precisely about what you need and why.

**The person it doesn't work for** is equally important to identify. A busy cardiologist who has never opened a terminal and has fifteen minutes between patients is not going to build an app with AI. Not because they lack the domain knowledge — they have more of it than I do — but because they lack the time, the comfort with technical iteration, and the tolerance for a process that requires multiple sessions of focused conversation. If your instinct is "just build it for me," you want a developer, not an AI assistant. AI doesn't eliminate the need for clear thinking about requirements — it makes that need more acute, because it will build exactly what you tell it to, including your blind spots.

The distinction isn't technical skill versus no technical skill. It's this: can you describe your problem precisely enough that someone who knows nothing about your domain could verify whether a solution is correct? If yes, you can work with AI. If no — if correctness requires your ongoing judgment at every step — you can still work with AI, but you need to be in the loop for every iteration, not checking in at the end.

## The hard questions

There's a framework — from the Theory of Constraints community — for evaluating any new technology without getting seduced by the hype. Six questions, developed by Eli Goldratt and his collaborators, originally for enterprise technology but applicable to any tool that changes what's possible. What can the technology actually do? What limitation does it remove? What had people been doing instead? What assumptions need to change? I use it because it forces me to be concrete.

### 1. What is the power of the technology?

An AI coding assistant (in my case, Claude in the terminal) can write, debug, test, and refactor code through conversation. You describe what you want in natural language, it produces working code. It knows languages, frameworks, libraries, conventions. It can hold a spec in context, enforce constraints across a session, and catch its own mistakes when you point them out.

What it cannot do — yet — is know what you need. It can research whether breath retention is dangerous for cardiac patients (and it will find the answer if you guide the inquiry), but it cannot originate the question from lived experience. It has a surprisingly good sense of design, but it needs to know what it's designing for — the context, the stakes, the non-negotiables. It can suggest reasonable priorities, but you have to pick. Anyone who has watched a developer build something technically correct but functionally wrong already knows this gap.

### 2. What limitation does it eliminate?

**Building quality software has historically required either a team or years of solo craft.** If you're a domain expert — a doctor, a patient, a researcher, a teacher — and you see a gap that no commercial product fills, you're stuck. You can file a feature request and hope. You can hire a developer and pay. You can learn to code over months and years. Or you can give up and adapt to tools that don't quite fit.

AI eliminates this limitation. A person who understands their problem deeply, can think clearly about requirements, and can evaluate whether a solution is correct can now build working, tested software that solves their problem — in days rather than months. The bottleneck was never the idea or the domain knowledge. It was the translation layer — turning intent into working code.

To make this concrete: I estimated what Breathe CLI would have cost to build the traditional way — a non-developer hiring a freelance Python developer. The coding itself might be 60–80 hours. But code is only part of the work. Add the clinical research and safety validation. Add the testing, the documentation grounded in physiology, the packaging for PyPI and Homebrew. Add the communication overhead — revision loops where "this feels wrong" doesn't fit in a Jira ticket. The realistic total: 170–220 hours, $12,000 to $40,000, spread over three to four months. I spent a few sessions with Claude Code. Maybe 5–10 hours of my time. The subscription cost was negligible.

But the ratio isn't really the story. Without AI, Breathe CLI would never have been built. Not by me, not by anyone. The market is too small, the domain knowledge too specific, the cost too high. This isn't unique to cardiac patients or breathing exercises. Any domain expert sitting on unsolved, hyper-specific problems faces the same economics. What changes at this cost structure is not productivity — it's possibility. A new category of software that could not have existed before. I call this a Market of One — software built by a domain expert to solve their own problem, where the traditional cost of building would dwarf the value to any market willing to pay.

**The excavator problem.** An excavator is a powerful force multiplier. It can dig a hole for your swimming pool in a fraction of an afternoon at a reasonable cost — work that would take days and be prohibitively expensive using manual labor alone. But if you're not a trained operator, you might accidentally crush a car parked nearby or crack your foundation. AI coding assistants are the same kind of force multiplier.

I could have easily built a breathing app that encodes patterns that are positively harmful to me — like the popular box breathing technique, which includes breath holds that can trigger syncope or arrhythmia in cardiac patients. If I hadn't had a modicum of cardiology knowledge, I would have built a tool that confidently guides me through something dangerous. The AI would have implemented it beautifully.

Even at the mechanical level, the risk is real. Partway through building Breathe CLI, I introduced two command-line flags that were logically inconsistent with each other. Claude Code didn't catch the design-level contradiction. It implemented exactly what I specified, and the app produced subtly wrong behavior that survived five rounds of debugging. The fix was two lines.

The lesson: AI will build precisely what you tell it to, including your mistakes. The domain expert isn't just the person who knows what the app should do. They're also the person who catches what the AI won't.

### 3. What workarounds exist today?

Before AI coding assistants, domain experts had five paths. Each one fails in its own way.

You adapt to bad tools. You use the breathing app that adds breath holds and just skip those parts manually. "Making it work" becomes a permanent tax on your attention.

You hire a developer. You spend $15,000 and three months explaining your domain to someone who has never lived in it. The result is technically competent and subtly wrong. Eventually you accept "close enough."

You file a feature request. It goes into a backlog with four hundred other requests. The product team prioritizes by market size. Your use case is not a segment that moves revenue numbers. Nothing happens.

You cobble something together. A bash script, a spreadsheet macro, a chain of browser tabs. Fragile, undocumented, untransferable.

You go without. The most common path and the least visible. You simply absorb the cost of not having the right tool. The problem doesn't go away — you just stop noticing it.

Five paths, all dead ends. If you recognized yourself in any of them, you already know why the next question matters.

### 4. What rules need to change?

Several assumptions need to collapse:

**"Software worth building has to serve a large market."** No. At this cost structure, the threshold for "worth building" drops to one — yourself. This isn't entirely new — David Skoll built [Remind](https://dianne.skoll.ca/projects/remind/), a calendar and reminder tool, in 1992 because nothing else fit his workflow. It's been maintained for over thirty years. But Skoll is a software developer. The pattern has always existed; it was just locked behind a skill gate that most domain experts couldn't pass.

**"Users should not build their own tools."** That used to be true — when building was hard and fragile. But if an AI can enforce code quality, write tests, maintain consistency, and catch regressions, the output of a domain-expert-plus-AI collaboration can be as good as — sometimes better than — what a team of generalists produces. Better, because the person specifying the requirements actually lives with the problem.

**"I need to learn to code first."** Not exactly. You need to learn to think precisely about requirements, edge cases, and failure modes. You need to evaluate output critically. These are skills, but they're different skills than writing Python from scratch. A cardiology patient who understands Valsalva physiology, reads the Bernardi papers, and can articulate exactly why breath holds are dangerous doesn't need to know how `select.select` works. They need to know what their app must never do.

### 5. How to design the technology to avoid resistance?

Goldratt's fifth question asks how to design the application of the technology so it doesn't create new problems. (The original question is narrower — what changes does the technology itself need? Schragenheim later broadened it to include adoption resistance.)

The resistance comes from two directions — upstream and downstream.

**Upstream: your own resistance.** If you've read this far and still haven't tried it, this is probably why. The people who would benefit most from AI-assisted building are often the least likely to try it. You don't think of yourself as a builder. You've internalized the assumption that software is someone else's job — that your deep knowledge of cardiac physiology, or supply chain dynamics, or special education needs, doesn't translate into something you could build. The technology needs to meet you where you are: in natural language, in conversation, without requiring you to think of what you're doing as "programming." That's what AI coding agents do well — you describe what you need, you evaluate what you get, you iterate. The skill is thinking clearly, not writing code.

**Downstream: the user's trust.** "Can I trust code written by AI?" This is a legitimate concern, and the answer has to be: look at the code. The entire point of single-file, no-dependency, MIT-licensed software is that you can read every line. The safety constraints are in the source. The clinical citations are checkable. The tests are runnable. Trust is earned through transparency, not authority — and this is easier, not harder, when the codebase is 700 lines instead of 70,000.

### 6. What's the strategy for a Market of One?

Goldratt's sixth question is about strategy. Traditional software strategy starts with market research. Market of One inverts it: solve your own problem first, then let the market find you — or not.

**Build:** Solve your own problem first. Don't speculate about what others might need. If you have a condition, you are the spec.

**Capitalize:** Publish openly. MIT license, public repo, package managers (pip, Homebrew). The "customer acquisition cost" is zero because you're not selling anything. If someone with the same condition finds it useful, the investment has paid for itself.

**Sustain:** Keep the scope small. A single-file app with no dependencies has dramatically less maintenance than a typical software project. There's no infrastructure to rot, no subscription to expire, no team to coordinate. It stays useful as long as Python runs. I've since built a second tool — for managing medication orders and prescriptions — using the same approach. The pattern scales to adjacent problems. If you've ever hesitated to share something you built because it felt too small or too personal, this is the strategy that makes sharing safe.

"Market of one" is a deliberate hyperbole. I built this for myself, not for a market. The project is a success even if I'm the only person who ever uses it. But somewhere in the long tail of people who are both cardiac patients and terminal users, someone might find it useful. That's a side benefit, not the goal. The goal was to solve my own problem. The idea that this is now possible — and worth doing — is what's worth sharing.

## The next bottleneck

If this pattern scales — and I believe it will — then the new bottleneck isn't building. It's discovery. I published Breathe CLI on GitHub, PyPI, and Homebrew. I submitted it to Google Search Console. But if another cardiac patient somewhere built a different tool that solves a problem I haven't thought of yet, how would I ever find it? There are awesome-lists on GitHub and Show HN posts, but they're organized by developers for developers — by language, by tool category, by technical novelty. Not by the human situation that motivated the code. That's the infrastructure gap this kind of software will eventually need — and it doesn't exist yet.

"If building is nearly free, why not just build your own version?" Because the real loss isn't failing to find someone else's code. It's failing to discover what problems are solvable. Another cardiac patient's tool might encode clinical knowledge I don't have — solving a problem I haven't conceived of yet. The constraint moved from building to conceiving. Discovery serves the new constraint. This is the logic Goldratt applied to technology development: breakthroughs come from finding what already exists and seeing where it falls short. Without discovery, every domain expert starts from zero.

---

For the first time since my diagnosis, there is something I built myself — a small piece of agency in a situation defined by dependence on medications, doctors, and devices. I can open a terminal and breathe slowly for fifteen minutes, paced by an app that refuses to let me do anything that might make things worse — an app that exists only because, for the first time, building it cost less than needing it.

---

## Addendum: Getting started

Let me be precise about what this requires. AI doesn't bring programming to the masses — it brings programming to people who think like engineers about their own problems. The same promise as "English-like" programming languages, which made syntax easier but didn't make *thinking* easier. Developing software with AI is still programming — but at a different level of abstraction. It requires the same disciplined mindset as traditional development, without the overhead of learning the intricacies of a specific language. Python abstracts away assembly language. AI abstracts away Python. But the intellectual discipline needs to be there, or you will build a frankenapp.

Here is what the process looks like:

**Start with a painful problem you can verify.** Not a vague wish — a problem you live with, where you will recognize a correct solution when you see one. If you can't tell right from wrong in the output, you're not ready.

**Research first.** You can farm out the research to AI. Ask it to survey the domain, find relevant prior art, identify constraints and risks. This is where AI is safest — it's gathering information, not building anything yet.

**Spec before code.** Before any code gets written, develop a specification conversationally. The first version doesn't need to be perfect, but it must clearly articulate direction and boundaries — what the tool does, what it must never do, what counts as success. You are working out what you want before you tell the machine to build it. The spec is a launching pad, not a contract — something to establish intent, not something you'll maintain in sync with the code.

**Tests before code.** Once the spec feels right, have the AI write tests. You don't need to know anything about test frameworks. The incantation is: "use the TDD approach." Test-driven development means the tests define correct behavior before any implementation exists. This is your safety net — the thing that catches the excavator before it hits the house.

**Then let it code.** Only now does the AI write implementation. Let it choose the language — it will probably pick Python. Don't panic if you've never written a line of Python. I haven't. But I can produce a 700-line app without ever touching the code manually, because I'm working at a different level of abstraction: specifying, evaluating, correcting.

There's more to the workflow than I can cover here — the best way to learn is to start with a problem you can verify and let the iteration teach you the rest.

---

*[Breathe CLI](https://github.com/marekkowalczyk/breathe-cli) is free, open source, and available via `pip install breathe-cli` or `brew tap marekkowalczyk/breathe && brew install breathe`. It is not a medical device.*

*The six questions framework comes from Goldratt, Schragenheim, and Ptak's* Necessary But Not Sufficient *(2000), with refinements by Schragenheim published through TOCICO.*

---

*[Marek Kowalczyk](https://orcid.org/0009-0008-3874-6736) is a Theory of Constraints consultant, adjunct professor, and cardiac patient based in Warsaw, Poland.*
