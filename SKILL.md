---
name: ai-project-os
description: Initialize and operate a lightweight project-level AI collaboration layer with progressive context loading, project facts, task routing, failure memory, and delivery validation.
---

# AI Project OS

## First principles

Let any AI enter a project and, based on the project's own verified information, keep delivering usable, verifiable, reproducible results with the minimum necessary capabilities — without overstepping.

Six rules follow:

1. **The project is the source of truth**: rules, context, skills, MCP configuration, and versions live with the project, not in a personal global environment.
2. **The goal is product delivery**: the measure is whether users can use the result and whether it can be accepted — not how much code was generated.
3. **Only the minimum necessary capabilities**: load, install, and enable only what the current project actually needs.
4. **Evidence over claims**: distinguish implementation, engineering verification, and product acceptance; never raise the completion level without evidence.
5. **Capability is not permission**: recommended ≠ installed, installed ≠ enabled, enabled ≠ authorized to run production operations.
6. **AI is bound by the project**: never expand scope, modify production, handle secrets, or make high-risk decisions on the user's behalf.

There is only one question for adding a feature: does it help AI understand the project more accurately, complete real tasks more reliably, or make delivery easier to verify? If it does none of the three, it does not go in.

## Entering a project

1. Read the project's `AGENTS.md`.
2. Read `.agents/skills/project-memory/SKILL.md` when it exists.
3. Match the request against `docs/ai/routes.json`.
4. Load only the files listed by the matching route.
5. Current user instructions, code, tests, and project-native rules take precedence over memory entries.

Do not load all project memory files by default; progressive loading is the primary context control.

The generated `AGENTS.md` follows the project-level instruction file convention (introduced by OpenAI Codex, supported by GitHub Copilot and others): the instruction file lives at the repository root. The layer is scoped as `AGENTS.md` (project agreement) → `.agents/skills/project-memory/SKILL.md` (loading entry) → `docs/ai/` (facts).

## Advising adoption

When a user gives you this repository and asks how to use or adopt it:

1. Read `docs/getting-started.md` (or `docs/getting-started_zh.md` for Chinese).
2. Inspect the target read-only before recommending or writing anything.
3. Identify the Git roots, existing instructions, initialized project layers, and repository boundaries.
4. Recommend the smallest suitable initialization scope and explain fact ownership, generated files, limitations, and rollback.
5. Decide safe reversible details from evidence; ask the user only about choices that materially change the target, authority boundary, Git organization, or overwrite behavior.
6. Run `--dry-run` before initialization, then validate the applied result.

Never restructure repositories, overwrite existing instructions, enable optional capabilities, or commit secrets and absolute local paths as an implicit part of adoption.

## Initialization

Dry-run before writing into an existing project:

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

Then apply; existing files are not overwritten by default:

```powershell
python scripts/init_project_os.py --target <project-root>
```

`--force` only refreshes template and protocol files; the filled state files under `docs/ai/` (project facts, memory, capability manifest, and lock) are never overwritten — delete them manually to reset.

## Project memory contract

- `docs/ai/project.json`: stable project facts, fact sources, commands, quality gates, and risk boundaries.
- `docs/ai/routes.json`: request signals and the minimum context to load.
- `docs/ai/memory.json`: verified tool failures, user corrections, and recurrence-prevention records.
- `docs/ai/capabilities.json`: project-level Skill and MCP selections and their lifecycle state.
- `docs/ai/capabilities.lock.json`: locked source revisions and content or configuration checksums.
- `docs/ai/logs/`: concise evidence of meaningful operations and verification.

Write each fact into the file it best matches. Never write methodology manuals, chat transcripts, secrets, or guesses into project memory.

Memory is tightly coupled to code: after the code, tests, or approach a record depends on changes, re-verify that record; entries past `expires_at` must be reviewed and updated or removed, not reused.

## Conflict handling

When context, documentation, or code conflicts, check recency first; do not assume a contradiction by default. Use git to judge which side is newer: query each side's last change (`git log -1 --format=%cs -- <path>`), treating uncommitted local changes as newest; `verified_at` in `docs/ai/memory.json` judges how new a memory entry itself is.

1. Prefer the newer document: the newer side usually represents the current approach; the older side is not a second, parallel truth.
2. Re-review the older document: constraints, boundaries, and notes that remain valid may have been dropped during a switch; restore them into the newer document instead of discarding them wholesale.
3. Record only confirmed conflicts: when time cannot decide or a conflict is confirmed, follow the current user instruction and the facts in `docs/ai/project.json`, and record the resolution in `docs/ai/memory.json` `corrections` with `verified_at`.

## Product work protocol

For non-trivial product changes:

- Start from the user-visible outcome and real constraints; choose the simplest mechanism that closes the loop, not from available technology or a generic checklist.
- Before implementing, clarify the user, current flow, target flow, smallest complete scope, important failure paths, and acceptance evidence.
- Check UI, API, backend, data, transactions, idempotency, concurrency, indexes, performance, permissions, audit, and observability only when relevant.
- Classify adjacent issues as current blocker, required risk, or later improvement; implement only the first two.
- Lead with the conclusion in plain language; add technical detail only when it helps a decision, implementation, or verification.

## Operations

- Before running project commands, use the commands recorded in `docs/ai/project.json` and check related failures in `docs/ai/memory.json`.
- After a tool failure, correction, or recurring defect, record evidence only when it will change future behavior.
- Ask before production changes, destructive data operations, credential handling, and actions the project facts mark for confirmation.
- At delivery, separate implementation, engineering verification, and product acceptance, and report what remains unverified.

## Recommendation and installation capabilities

When the user needs an optional capability, read `references/recommended-integrations.json`.

- Treat Skills (prompt and workflow guidance) and MCP Servers (tool capabilities) separately.
- Recommend only entries that match the current intent or have project evidence; show source, maintainer, license, impact, and rationale.
- Recommendations are never installed or enabled automatically.
- After an explicit user choice, default to project-level installation: third-party skills go into the project's declared `skill_directory` (the layer's own entry stays fixed at `.agents/skills/project-memory`), and MCP configuration goes into the project's declared `mcp_config`. Both paths are declared in `docs/ai/capabilities.json`; template defaults are `.agents/skills` and `.codex/config.toml`, and other tools change their own pointers.
- Collection repositories install only the selected child skill; every installed or configured capability is written to the project manifest and lock file.
- After the user's choice and before installation, re-verify the upstream source and license.

## Validation

```powershell
python scripts/validate_project_os.py --target <project-root>
python scripts/validate_project_os.py --target <project-root> --strict
python scripts/self_check.py
```

Validation covers required files, JSON structure, route safety, memory entry contract and expiry, local-only ignore rules, unfilled placeholders, possible secrets, capability scope and manifest/lock drift, plus directory hashes of locked skills and hashes of managed MCP config blocks.

Human-readable Chinese translation: [SKILL_zh.md](./SKILL_zh.md)
