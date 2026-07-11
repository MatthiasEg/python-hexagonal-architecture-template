# Specs

Lightweight, plan-driven development for non-trivial changes. For anything bigger than a
one-file fix, write a short spec before writing code — it forces the design decisions to the
surface and gives an agent a checkable plan.

- [`TEMPLATE-spec.md`](TEMPLATE-spec.md) — the design: what and why, the approach, non-goals.
- [`TEMPLATE-tasks.md`](TEMPLATE-tasks.md) — the ordered, checkable task breakdown.

Copy the templates into a dated file (`YYYY-MM-DD-short-name-spec.md`), fill them in, get
agreement on the spec, then execute the tasks. Each task should end at a green
`uv run poe check`. These templates are intentionally minimal; delete sections that do not
apply rather than padding them.
