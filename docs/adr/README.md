# Architecture Decision Records

Short documents capturing an architecturally significant decision: the context, the choice,
and, most importantly, the alternatives that were rejected and why. Read these before
changing the architecture or the validation loop; they exist so a decision is not silently
reversed by someone (human or agent) who never saw the tradeoff.

Format is a trimmed [MADR](https://adr.github.io/madr/). Copy the template,
[`0000-adr-template.md`](https://github.com/MatthiasEg/python-hexagonal-architecture-template/blob/main/docs/adr/0000-adr-template.md),
for a new record, give it the next number, and never edit an accepted ADR to reverse it.
Supersede it with a new one and mark the old one `Superseded by ADR-XXXX`.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-enforce-hexagonal-boundaries-with-import-linter.md) | Enforce hexagonal boundaries in CI with import-linter | Accepted |
| [0002](0002-validation-loop-tool-selection.md) | Validation-loop tool selection and exclusions | Accepted |
| [0003](0003-unit-of-work-commit-authority.md) | The UnitOfWork is the sole commit authority | Accepted |
| [0004](0004-utc-timestamps-owned-by-the-domain.md) | Entities own their UTC timestamps | Accepted |
