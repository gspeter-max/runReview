---
name: ultrathinking
description: >
  Activate this skill when the task is complex, ambiguous, involves
  system design, architecture decisions, debugging hard problems,
  multi-step reasoning, performance tradeoffs, or any situation where
  jumping to the first answer would produce a poor result. Trigger
  phrases include: "think deeply", "ultrathink", "reason through",
  "think step by step", "plan carefully", "what could go wrong",
  "analyze tradeoffs", "design this system".
---

# Ultrathinking Protocol

When this skill is active, you are operating in maximum reasoning mode.
Do NOT jump to a solution. Follow every step below in order.

## Phase 1 — Understand before anything else

Before writing a single line of code or giving any answer, state in
your own words:
- What is the actual problem being solved?
- What constraints exist (performance, compatibility, team conventions)?
- What is NOT being asked? (scope boundaries)
- What would a wrong or lazy answer look like?

## Phase 2 — Generate multiple approaches

Generate at least 3 fundamentally different approaches to the problem.
For each approach, write:
- Core idea in one sentence
- Main advantage
- Main risk or tradeoff
- Scenarios where this approach fails

Do not evaluate them yet. Just generate.

## Phase 3 — Challenge your own thinking

For each approach ask:
- What assumption am I making that could be wrong?
- What edge case does this not handle?
- What happens at 10x scale?
- What does this cost to maintain in 6 months?

## Phase 4 — Synthesize the best path

Now pick the best approach or a hybrid. Explain:
- Why this approach wins given the specific constraints
- What you are consciously trading off
- What you would do differently if constraints changed

## Phase 5 — Plan before executing

Write a numbered implementation plan BEFORE writing any code or making
any changes. Each step should be specific and verifiable. Get
confirmation if needed before proceeding to execution.

## Phase 6 — Verify after executing

After any implementation:
- Run tests or shell commands to confirm correctness
- State what you verified and what you could not verify
- Flag any remaining uncertainties explicitly

## Mindset Rules

- Slow down deliberately. A 30-second pause to think is worth 30
  minutes of debugging wrong code.
- If something feels too easy, you have probably missed a constraint.
- Never say "this should work" — either verify it or say why you
  cannot verify it right now.
- If you are unsure, ask one targeted question rather than proceeding
  with an assumption.