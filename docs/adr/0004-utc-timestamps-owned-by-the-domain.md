# ADR-0004: Entities own their UTC timestamps

- **Status:** Accepted
- **Date:** 2026-07-05

## Context

`created_at` / `updated_at` can be set in three places: the database (server-side
`DEFAULT now()` / triggers), the ORM model (SQLAlchemy `default=`/`onupdate=`), or the domain
entity itself. Where they are set decides whether the domain is testable without a database and
whether timestamps mean the same thing across adapters. A related question is timezone: naive
local time is a recurring source of bugs.

## Decision

The domain `Entity` base class owns timestamps, in UTC:

- `created_at` and `updated_at` default to `datetime.now(UTC)` via field factories.
- Mutations produce a new entity through `with_updated_at()` (entities are frozen/immutable), so
  `updated_at` advances as part of the domain operation — e.g. `Task.transition_to()` refreshes
  it.
- Timestamps are always timezone-aware UTC. Display-timezone conversion is a presentation
  concern, not a storage one.

## Alternatives considered

- **Database-generated timestamps** (`server_default=func.now()`, an `onupdate` trigger).
  Authoritative and monotonic, but the domain can no longer construct a fully-formed entity
  without a round-trip, unit tests need a database or fixtures to see timestamps, and a second
  persistence adapter (in-memory, another store) would have to reimplement the behavior.
  Rejected: it drags a domain property into infrastructure.
- **ORM-level defaults** (SQLAlchemy `default=`/`onupdate=`). Better than DB triggers but still
  ties timestamp semantics to one adapter; the in-memory repository used in unit tests would
  behave differently from Postgres. Rejected for the same reason.
- **Naive local time.** Ambiguous across environments and DST. Rejected outright.

## Consequences

- Entities are fully valid and testable in memory, with meaningful timestamps, no database
  required — which is what lets the use-case unit tests run with zero mocks.
- All adapters agree on timestamp semantics because they come from one place.
- The tradeoff: timestamps come from application wall-clock, not a single database clock, so
  they are not guaranteed monotonic across hosts with skewed clocks. For audit-grade ordering
  you would add a database-side authority; for typical application needs, domain-owned UTC is
  the right default. If that changes, supersede this ADR.
