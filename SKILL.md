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

For every task performed inside an initialized project, apply this protocol automatically; do not require the user to invoke `$ai-project-os` explicitly.

1. Identify the active collaboration root: reuse a covering workspace layer rather than equating every Git root with a project. Read its `AGENTS.md` and the applicable repository-native instructions.
2. Read `.agents/skills/project-memory/SKILL.md` at that collaboration root when it exists; resolve memory and route paths from that root, not the shell's current directory.
3. Match the request against `docs/ai/routes.json`.
4. Load only the files listed by the matching route.
5. Current user instructions, code, tests, and project-native rules take precedence over memory entries.

Do not load all project memory files by default; progressive loading is the primary context control.

The layer is scoped as `AGENTS.md` (project agreement) → `.agents/skills/project-memory/SKILL.md` (loading entry) → `docs/ai/` (facts). Its root may be one repository or a parent workspace containing several repositories for one product; Git roots remain code/version boundaries.

## Advising adoption

When a user gives you this repository and asks how to use or adopt it:

1. Read `docs/getting-started.md` (or `docs/getting-started_zh.md` for Chinese).
2. Inspect the target read-only before recommending or writing anything.
3. Identify Git roots, existing instructions, layers in ancestors and relevant children, and the product boundary. For one product with multiple repositories under a common parent, use one layer versioned in that parent's own Git repository. Reuse existing parent Git or include establishing it in the confirmed adoption plan. Unrelated products need separate scopes.
4. Reuse a covering layer; do not initialize every child Git repository. Recommend the smallest suitable initialization scope and explain fact ownership, generated files, limitations, and rollback. Keep repository facts task-routed, commands explicit about their repository working directory, and Git operations inside the owning repository.
5. Decide safe reversible details from evidence; ask the user only about choices that materially change the target, authority boundary, Git organization, or overwrite behavior.
6. Run `--dry-run` before initialization, then validate the applied result, its own Git root, and version history. File generation or an empty Git repository is only preparation. Record the reviewed layer as a local commit according to the project workflow; report uncommitted records as pending. An existing user request to establish parent Git is sufficient authorization within its confirmed scope.

Never restructure repositories, overwrite existing instructions, enable optional capabilities, or commit secrets and absolute local paths as an implicit part of adoption. Existing child layers need backup, fact/path/command reconciliation, and parent validation before any removal; see the getting-started guide.

Open the AI at the parent workspace for shared-layer use. A session started at a child Git root may not discover parent instructions, skills, or MCP configuration; explicitly load the parent entry or use a user-chosen thin pointer instead of duplicating the layer. Tool configuration still needs its own discovery and trust checks.

Parent Git owns the shared layer and selected workspace documents; code stays in each child Git repository. Inspect the parent index, exclude independent children with root-anchored ignores, and stage only confirmed files. Ignores do not untrack existing content. Do not add accidental child Git links, assume child revisions are pinned, or configure remotes/push without the corresponding request.

## Initialization

Resolve every `scripts/...` command from this skill kit's directory, not the target or current shell directory. Pass the confirmed collaboration root as `--target`; when running elsewhere use resolved script and target paths. Dry-run before writing into an existing project:

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

Then apply; existing files are not overwritten by default:

```powershell
python scripts/init_project_os.py --target <project-root>
```

The initializer only prepares layer files; it does not initialize Git, stage, commit, or push. Establish and verify the root's Git ownership as part of adoption. `--force` only refreshes template and protocol files; filled state files under `docs/ai/` are never overwritten — delete them manually to reset.

The initializer refuses a second layer below an existing ancestor layer, including during dry-run and with `--force`. Use `--allow-nested` only for an explicitly chosen independent project; it does not merge or migrate layers. Route targets must remain inside the collaboration root after path resolution.

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

When context, documentation, or code conflicts, check recency first; do not assume a contradiction by default. Query each tracked source's last change in its owning Git repository (`git log -1 --format=%cs -- <repo-relative-path>`), treating uncommitted local changes as newest; `verified_at` judges memory recency. For untracked or preparation-stage files, use verified source dates or report unknown recency rather than inventing Git evidence.

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
