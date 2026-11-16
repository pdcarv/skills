---
name: tour
description: >-
  Writes a guided tour of the current repository for a developer who wants to understand it
  fast: reads the code, builds a graph of domain concepts and how they connect, puts the
  most-connected concepts at the core of an onion and works outward through services and
  adapters to the external systems the code calls or depends on. Each ring becomes a
  narrative chapter in plain words, with an analogy and a real code excerpt per concept, in
  one self-contained HTML page with an onion diagram. Afterwards it offers an optional quiz
  page for recall practice. Use when someone is new to a project or asks to understand,
  explore, learn or get onboarded to a codebase, asks for a tour or an explanation of a
  repo, how a project fits together or where to start reading. For reference docs aimed
  at maintainers, use system-docs.
license: MIT
metadata:
  category: "documentation/knowledge"
  sources: "see Sources section"
---

# Tour

A developer new to a repo wants a mental model before they read code: the few ideas everything else is built on, then the layers that use those ideas, then the edges where the system meets the world. Teach it like a good technical book: from the center out, one idea at a time, in plain sentences, with real code to anchor each idea. How connected a concept is decides how much care it gets.

**Side effects:** writes one HTML file (default `docs/tour/index.html`; confirm the path before writing) and, only if the user accepts the learning step, `docs/tour/quiz.html` beside it. Reads the code; runs `scripts/inject_excerpts.py`; may render the page to an image and spawn a fresh-context subagent as the test reader. Never edits code, posts or commits.

## When to use

- Someone is new to a repo (or a subsystem of one) and wants to understand it quickly.
- "Give me a tour", "explain this codebase", "how does this project fit together", "where do I start reading?"

## When not to use

- Maintainer reference (where to change things, invariants, run commands): `system-docs`.
- Learning a general topic rather than this code: a teaching or research skill.
- One specific question about the code ("where is X handled?"): answer it directly.

## Inputs to gather

- Scope: the whole repo, or one subsystem. Above roughly 300 source files, propose a subsystem before reading further.
- The reader: what languages and frameworks they already know (skip explaining those) and what they want to do first, if anything (that chapter gets an extra pointer).
- The output path; check whether a tour already exists there and update it instead of starting over.

## Procedure

1. **Survey.** Read the README, build manifests, entry points (main, CLI, server setup, handlers), the directory tree, and deployment or infra files. List vendored, generated and test-fixture directories to exclude; they inflate every count.
2. **Build the concept graph** in your notes, not in the repo.
   - A node is a domain concept: a thing or rule the system is about (an order, a forecast, a reconciliation), usually a type, table, aggregate or module named after it. Files are evidence, not nodes; one concept can span several files.
   - An edge is a real use: holds, creates, transforms, calls, reads, publishes. Record the code location for each.
   - Plumbing (logging, config loading, utils, error wrappers, framework glue) is not a node. It would win any count while explaining nothing. List it in one line in the appendix.
3. **Place the rings.** Rank concepts by connections. Then place each by what it depends on:
   - Core: the most-connected concepts that depend on nothing outside the domain. Usually 2-5.
   - Domain rules and services: logic built only on core concepts.
   - Application: use cases that orchestrate domain work for one request, job or command.
   - Adapters: code that turns the outside world into domain calls and back (HTTP, CLI, DB, queues, files, SDK clients).
   - External systems, outside the onion: every service, database, API or platform the code calls, is called by, or needs to run. Find them in clients, connection strings, env vars, config, IaC and docker-compose, not only in imports.
   Real code rarely follows the onion exactly. Place concepts by meaning, and when the code points a dependency outward (domain importing the ORM, for example), say so in the chapter: it is something a newcomer must know. Placements a reader could dispute (a `Config` type, a struct that is both data and orchestration) get one sentence saying why the concept sits in that ring.
   Bugs you notice along the way go in "Where the code bends the rules" as observations with their `path:line`. Do not write probe tests or run experiments to confirm them: the reader asked for understanding, and a bug hunt eats the time the teaching needs.
4. **Write the book**, one chapter per ring from the center out, then a chapter on external systems. For each concept, in this order:
   - its name and a one-sentence everyday analogy, plus where the analogy stops working;
   - a plain definition in one or two sentences, using the code's own names;
   - why it exists: what would be harder without it;
   - one real excerpt of 15 lines or fewer, written as a marker `<!-- excerpt path:start-end -->` on its own line (step 6 fills it in), then two or three sentences on what to notice;
   - its connections, each linked to that concept's section.
   In the Application chapter, also trace one request, event or command end to end: a numbered list of the concepts it touches, in order, each linked to its section. Without it the reader has to assemble the flow from scattered sections.
   The top-ranked concepts get all of this. A concept with one or two connections gets a short paragraph. For each external system, give the direction (we call it, it calls us, we need it to run), the protocol, where it is configured, and what the code does when it fails, if the code shows that. Neighbours that are not services (the runtime, environment variables, a person copying a token by hand) get one line saying what they are and why the code needs them, without the protocol and config fields.
5. **Voice.** Narrative, second person, conversational, like an O'Reilly book. Short sentences, one idea each. Define a term before using it, and link each first use to its definition. No unexplained acronyms. Earn every sentence: the analogy and the "why" carry the teaching, not adjectives.
6. **Build the page**: one self-contained HTML file, with inline CSS and no external requests, so it opens offline and diffs in git. Include: a short preface (what the system does, for whom, its boundary); an inline SVG onion with concentric rings, the concepts labelled in each and external systems outside, each label linking to its section; the chapters; a glossary. Support light and dark with `prefers-color-scheme`. Write the page as a template in a scratch folder, then fill the excerpts from the current files: `python3 <this skill's folder>/scripts/inject_excerpts.py --repo <repo root> <template> <out.html>`. It escapes the code, adds the `path:line` caption, and refuses missing files, bad ranges and excerpts over 15 lines. Re-run it after every edit to the template, never hand-edit the output.
7. **Look at the diagram.** Render the page to an image with a headless browser screenshot and view it, if you can view images. With no browser available, extract the SVG into its own file and render only that (ImageMagick `magick`, or `qlmanage -t` on macOS). Fix overlapping, clipped or unreadable labels; a crowded ring means too many labels, so keep the top concepts and list the rest in the chapter.
8. **Verify** (see below), then present the page with its path.
9. **Offer the learning step.** Ask whether the reader wants to work through what they learned. If yes, write `quiz.html` beside the book, in the same style: 2-3 questions per ring from the center out, mixing recall ("what does X hold?") with tracing ("a request arrives at Y; which concepts does it touch, in order?"). Use four options of equal length with the correct position varied, and give feedback on the spot (a few lines of inline JS) with a link back to the section that explains the answer. Keep no progress between sessions.

## Verification

- `inject_excerpts.py` ran on the final template without errors; any `path:line` written outside an excerpt points to an existing line.
- Every concept in the graph appears in the book. Nothing at the core is plumbing.
- Every external system found in step 3 is in the last chapter and outside the onion in the diagram.
- The page opens with no network requests (grep for `http` in `src=` and `href=` other than in-page links).
- Fresh-reader test: give a fresh-context subagent only the HTML and 3-5 newcomer questions ("what is the central idea?", "what happens when a request arrives?", "what breaks if <external system> is down?"). Check its answers against the code and fix the book where it guessed or got them wrong. One round: fix and move on, do not re-test, because each round re-reads the whole page and the gains drop off fast.
- In the quiz, every correct answer is supported by the linked section.

## Gotchas

- **Utilities at the center.** Raw import counts crown `utils` and `logger`. Count domain concepts, not modules.
- **Framework as concept.** "The Express app" or "the Django ORM" is not this system's idea. Explain what the system does with them.
- **Files as chapters.** A tour that walks the directory tree teaches the folder layout, not the model.
- **Hidden external systems.** A dependency known only from an env var or a Terraform resource is still a dependency, and often the one that breaks at 3 a.m.
- **Analogies that mislead.** Every analogy breaks somewhere; saying where is part of the teaching.
- **Prose bloat.** "Narrative" means flowing, not long. If a paragraph has no fact the reader didn't have, cut it.

## Output

The page follows this outline:

```text
Preface            what the system does, for whom, its boundary; how to read this tour
The map            inline SVG onion; every label links to its section
1. The core        one section per core concept: analogy, definition, why, excerpt, connections
2. Domain rules    ...
3. Application     ... plus one request traced end to end
4. Adapters        ...
5. The neighbours  each external system: direction, protocol, config, failure behaviour
Where the code bends the rules   outward dependencies and other surprises
Glossary           every term, one line, linked to its section
Appendix           plumbing left out of the graph; scope and exclusions
```

Then a short reply with the path, and the question about the learning step.

## Sources

- Jeffrey Palermo, "The Onion Architecture: part 1" (domain model at the center, all coupling toward the center, UI and infrastructure at the edge), 29 Jul 2008, read Nov 2026: https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/
- Alistair Cockburn, "The Hexagonal (Ports & Adapters) Architecture" (inside vs outside; adapters connect users, tests, databases and other systems), 4 Sep 2005, read Nov 2026: https://alistair.cockburn.us/hexagonal-architecture/
- Matt Pocock, `teach` skill (lesson-then-quiz structure; equal-length options, varied answer position, immediate feedback), read Nov 2026: https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md
- Roediger and Karpicke, "Test-enhanced learning", Psychological Science 17(3), 2006 (retrieval practice improves retention over re-reading). Unverified: the article page could not be fetched in Nov 2026: https://doi.org/10.1111/j.1467-9280.2006.01693.x
