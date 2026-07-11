# Spec: <title>

- **Date:** YYYY-MM-DD
- **Status:** Draft | Approved | Done

## Problem

What are we solving, and for whom? Why now? State the problem before any solution.

## Approach

The design in a few paragraphs. Which layers change (domain / application / infrastructure)?
Which ports get added or changed? Reference the `Task` slice and any relevant ADR. If the
change touches the architecture or the validation loop, link or add an ADR.

## Non-goals

What this explicitly does not do. Guard the baseline non-goals (no auth, rate-limiting, queue,
or LLM adapter unless the spec is specifically about adding one as a recipe).

## Risks & open questions

Anything that could make this harder than it looks, and anything that needs a decision before
starting.

## Definition of done

The observable outcome, plus: `uv run poe check` green, coverage above the floor, docs/ADRs
updated if the decision is architecturally significant.
