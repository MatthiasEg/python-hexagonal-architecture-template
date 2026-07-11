# Comparison

How this template differs from the popular FastAPI starting points. The honest summary: the
big templates win on trust and breadth; none of them enforce a hexagonal boundary, and that is
the specific gap this fills.

| | This template | [full-stack-fastapi](https://github.com/fastapi/full-stack-fastapi-template) | [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices) | [fastapi-clean-example](https://github.com/ivan-borovets/fastapi-clean-example) |
|---|---|---|---|---|
| Hexagonal / ports & adapters | Yes | No (layered, ORM-coupled) | N/A (a guide, not a repo) | Yes |
| Boundary **enforced in CI** | Yes, import-linter | No | No | No, folder conventions only |
| Scaffoldable "use this template" | Yes | Yes | No | No (an example) |
| Agent-native (`AGENTS.md`, runbook, deterministic loop) | Yes | No | No | No |
| Full-stack (frontend, auth, email) | No (by design) | Yes | N/A | No |
| Package manager | uv | Poetry/pip | N/A | uv |

## When to use this

You want a backend where the architecture is real and stays real: the domain never imports the
ORM, and CI proves it. You want AI agents to add features by mirroring a worked example and
self-verifying against one command. You are happy to add auth, a frontend, or a task queue
yourself when you need them, rather than starting with them.

## When **not** to use this

- **You want a full-stack app out of the box:** React frontend, auth, email, Docker Compose
  for everything. Use
  [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template); it is
  excellent at that and this template deliberately is not.
- **You want a simple CRUD service and find layered architecture to be overhead.** Hexagonal
  architecture earns its keep when business logic is non-trivial and long-lived. For a thin
  wrapper over a database, the indirection is a cost without much return, and
  [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices) is a better
  mental model.
- **You need something other than Postgres/SQLAlchemy** and do not want to swap the driven
  adapters. You can, since that is what ports are for, but it is work you would be signing up for.

The non-goals are deliberate: no auth baseline, no rate-limiting, no task queue, no LLM adapter.
Those are documented as recipes to add via a port, not defaults to carry.
