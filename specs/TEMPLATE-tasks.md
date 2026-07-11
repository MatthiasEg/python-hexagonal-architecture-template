# Tasks: <title>

Ordered so each task depends only on the ones above it, domain-outward (see
`docs/adding-a-feature.md`). Each task is small enough to finish and verify on its own.

- [ ] 1. Domain — entity + rules + unit test
- [ ] 2. Output port + in-memory fake + contract test
- [ ] 3. Input ports
- [ ] 4. Use cases + unit tests (in-memory repo, no mocks)
- [ ] 5. SQLAlchemy model + migration (review DDL, `migration-lint`)
- [ ] 6. Postgres repository adapter + integration test
- [ ] 7. API DTOs + controller (bound DTO fields to column limits) + integration test
- [ ] 8. `uv run poe check` green; docs/ADRs updated

Adapt the list to the actual change; delete steps that do not apply. Keep the invariant: the
last task is always a green validation loop.
