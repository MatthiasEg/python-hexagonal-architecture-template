---
name: add-migration
description: Use when a SQLAlchemy model changed and the schema needs a new Alembic revision. Autogenerate it, review the DDL by hand, and lock-safety-lint it with Squawk.
---

# Add a database migration

Alembic autogeneration is a draft, not an authority. Always read the generated DDL before
committing it, and lint it for production lock-safety.

## Steps

1. Make the model change in `src/app/infrastructure/db/models/`.
2. Autogenerate the revision:
   ```bash
   uv run poe db-revision -m "short description"
   ```
   This needs a reachable database (`APP_DATABASE_URL`) so Alembic can diff the live schema.
3. **Read** the new file in `src/app/infrastructure/db/migrations/versions/`. Autogenerate
   misses renames (it sees drop+add), server defaults, enum changes, and data migrations.
   Fix `upgrade()` and `downgrade()` by hand as needed.
4. Lock-safety lint the DDL:
   ```bash
   uv run poe migration-lint
   ```
   Squawk flags operations that take heavy locks on a live Postgres (e.g. adding a
   `NOT NULL` column with a default on an old Postgres, non-concurrent index creation).
   Split or rewrite flagged migrations. Requires the `squawk` binary on PATH
   (`brew install squawk`).
5. Apply and verify:
   ```bash
   uv run poe db-migrate
   uv run poe check
   ```

Commit the model change and the migration together: `feat(db): ...` or `chore(db): ...`.
