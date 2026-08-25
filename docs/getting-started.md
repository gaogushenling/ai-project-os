# Getting Started with AI Project OS

**English** | [中文](./getting-started_zh.md)

AI Project OS adds a small, versioned collaboration layer to an existing project. It gives an AI a project-owned entry point for facts, task routing, useful memory, capability state, and delivery checks. It does not replace the project's documentation, Git workflow, or engineering standards.

## What you need

- Python 3.11 or later
- This repository available to the AI or on the same machine as the target project
- Read access to the target project
- A clean or understood target working tree before files are written

Initialization does not reorganize repositories, install optional tools, enable MCP servers, or contact production systems.

## Give this repository to your AI

This is the recommended path. Share this repository together with the project you want to adopt, then say:

> Help me adopt AI Project OS in this project. Inspect it read-only first, recommend the right scope, show the dry-run result, and ask me only about decisions that materially change the result.

The AI should:

1. Read this guide and the repository-level `AGENTS.md`.
2. Inspect the target without changing it.
3. Identify existing Git roots, project instructions, `docs/ai/`, submodules, and relevant repository boundaries.
4. Recommend an initialization root and explain where shared and repository-specific facts should live.
5. Explain the generated files, current limitations, and rollback path.
6. Run a dry-run.
7. Ask the user only when the target, authority boundary, overwrite behavior, or Git organization requires a real choice.
8. Initialize after the scope is clear, validate the result, and explain daily use.

The AI may decide safe and reversible details from inspected evidence. It must not silently restructure Git repositories, overwrite existing instructions, write machine-specific paths into committed files, or enable optional capabilities.

## Manual setup

Clone the kit and enter its directory:

```powershell
git clone https://github.com/gaogushenling/ai-project-os.git
cd ai-project-os
```

Preview all planned files before writing:

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

Initialize after reviewing the preview:

```powershell
python scripts/init_project_os.py --target <project-root>
```

The initializer preserves existing files by default. Do not use `--force` until you have reviewed which template and protocol files it refreshes.

## Choose the project root

### Single repository

Use the Git repository root as `<project-root>`. The generated `AGENTS.md`, project-memory skill, and `docs/ai/` state are committed with that repository.

### Multi-repository workspace

Choose a repository that genuinely owns the shared product facts and cross-repository rules. Call it the control repository; this is a responsibility, not a requirement to become the Git parent of every other repository.

Keep ownership explicit:

- The control repository owns shared product facts, repository roles, cross-repository decisions, and shared acceptance rules.
- Each managed repository owns its code, commands, local engineering rules, and repository-specific verification.
- Machine-specific checkout locations belong in ignored local configuration, not committed project memory.

If no repository clearly owns shared facts, initialize each repository separately first. Creating a new control repository is a product and Git-organization decision, not an automatic setup step.

### Git submodules

Submodules are useful when a parent repository must pin and reproduce exact child revisions. They add operational cost: cloning, branch switching, updates, CI, and detached-HEAD behavior need deliberate handling.

AI Project OS may describe an existing submodule layout, but it must not convert repositories into submodules without an explicit user request.

### Ignored nested repositories

Ignored nested repositories are convenient for a local workspace because every child keeps an independent Git history. The parent does not record their remotes or revisions, so a fresh clone cannot reproduce the complete workspace by itself.

Use this as a local organization choice, not as evidence that the parent owns or versions the child repositories. Record only portable logical roles in committed files and keep local checkout mappings ignored.

Independent sibling repositories outside the initialized root remain outside the current route-safety boundary. Initialize them separately or keep cross-repository information in the control repository without adding out-of-root route targets.

## Complete the generated project facts

After initialization, review these files:

- `docs/ai/project.json`: product identity, owners, fact sources, repositories, commands, quality gates, and confirmation boundaries
- `docs/ai/routes.json`: task signals, files to load, and delivery gates
- `docs/ai/memory.json`: verified failures and corrections that should change future behavior
- `docs/ai/capabilities.json`: project-level skill and MCP locations plus installed capability state
- `AGENTS.md`: concise project agreement that every compatible AI can read

Replace all relevant `TODO` placeholders with verified project facts. Keep secrets, credentials, personal paths, and temporary observations out of committed files.

Validate the result:

```powershell
python scripts/validate_project_os.py --target <project-root>
```

When all placeholders are intentionally completed, use strict mode:

```powershell
python scripts/validate_project_os.py --target <project-root> --strict
```

Review the diff, then commit only the intended collaboration-layer files to the target repository.

## Daily use

Start the AI in the initialized project and describe the task normally. The project protocol automatically applies through compatible agents: they read `AGENTS.md`, enter project memory, and route the request, with no special command or repeated project selection required. For example:

> Investigate this request. Load only the relevant project facts, define the smallest complete outcome, and state the verification evidence before delivery.

During work, the AI should:

1. Read the project `AGENTS.md`.
2. Enter through `.agents/skills/project-memory/SKILL.md`.
3. Match the task in `docs/ai/routes.json` and load only the listed files.
4. Use commands and boundaries recorded in `docs/ai/project.json`.
5. Record only failures or corrections that will change later execution.
6. Separate implementation, engineering verification, and product acceptance in its final report.

Update project facts when the project changes. Do not use project memory as a conversation transcript or general documentation dump.

## Updating an initialized project

Pull or download a newer AI Project OS version, run `--dry-run` against the initialized project, and review the proposed additions. A normal re-run preserves existing files and filled state. `--force` refreshes template and protocol files but still protects the filled state files under `docs/ai/`; merge intentional local changes carefully.

Always validate after an update. Installed third-party skills and managed MCP blocks are checked against their lock hashes.

## Rollback and removal

There is no automatic uninstall command because initialization may preserve or coexist with project files that were already present. Use Git evidence to remove only what adoption actually changed:

1. Review `git status` and `git diff` before removing anything.
2. If adoption is still uncommitted, delete only the files that the dry-run identified as newly created. Manually undo additions to pre-existing files; never delete an entire file that existed before adoption.
3. If adoption was committed as a dedicated change, prefer `git revert <adoption-commit>` so shared history remains intact and the exact change is recoverable.
4. To reset filled project state, back it up if needed, remove the relevant state files under `docs/ai/`, and rerun initialization to generate defaults. Deleting state permanently discards the recorded project facts, memory, capability manifest, or lock data.
5. Remove installed skills or managed MCP blocks separately using `docs/ai/capabilities.json` and `docs/ai/capabilities.lock.json` as the ownership record. Removing the core layer does not automatically undo external tools or services.

After rollback or removal, run the relevant project checks and inspect the final Git diff. Do not use history rewriting or a destructive reset as the normal uninstall path.

## Safety boundaries

- Recommended does not mean installed; installed does not mean enabled; enabled does not authorize external or production actions.
- Existing instructions and project facts take precedence over generic examples after their authority and freshness are checked.
- Production changes, destructive data operations, credentials, external writes, and database changes require separate authorization.
- Route targets must remain inside the initialized project root.
- Portable committed files must not contain secrets or absolute local paths.

## Troubleshooting

### The dry-run reports existing files

Review the existing content and decide whether to keep it, merge the AI Project OS contract manually, or use `--force` for the refreshable templates. Do not overwrite project instructions blindly.

### Strict validation reports placeholders

Fill the reported fields with verified project facts. If a value is genuinely unknown, keep normal validation and report the unfilled item instead of inventing an answer.

### A route target is outside the project

Move the portable fact into the initialized project, initialize the other repository separately, or document only the logical relationship. Do not bypass the route-safety check with absolute paths.

### The AI does not automatically invoke the skill

Ask it to read the project `AGENTS.md` and `.agents/skills/project-memory/SKILL.md`, or explicitly say `Use $ai-project-os`. Tool support varies, but the committed project facts remain readable by any AI with file access.

### A capability cannot connect

Check the project capability manifest, local command availability, and required environment-variable names. Never paste secret values into `docs/ai/` or a prompt merely to make a connection work.

## Adoption checklist

- The initialization root and fact owner are explicit.
- Existing instructions were preserved or intentionally reconciled.
- Normal validation passes; strict validation is used when placeholders are complete.
- Commands and quality gates were verified rather than guessed.
- Multi-repository roles are logical and portable.
- No committed file contains secrets or absolute local paths.
- The user knows how to invoke AI Project OS and where future facts belong.
