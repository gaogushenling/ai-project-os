# Getting Started with AI Project OS

**English** | [中文](./getting-started_zh.md)

AI Project OS adds a small, portable collaboration layer to an existing project or product workspace. It gives an AI a project-owned entry point for facts, task routing, useful memory, capability state, and delivery checks. Its root can contain several independent Git repositories; it does not replace their documentation, Git workflow, or engineering standards.

## What you need

- Python 3.11 or later
- This repository available to the AI or on the same machine as the target project
- Read access to the target project
- A clean or understood target working tree before files are written
- A Git repository owned by the collaboration root and a reviewed local commit of shared records for complete adoption

The initializer only prepares files. It does not run `git init`, reorganize repositories, install optional tools, enable MCP servers, or contact production systems. Without Git at the collaboration root, a dry-run or file preparation is possible, but complete adoption is still pending.

## Give this repository to your AI

This is the recommended path. Share this repository together with the project you want to adopt, then say:

> Help me adopt AI Project OS in this project. Inspect it read-only first, recommend the right scope, show the dry-run result, and ask me only about decisions that materially change the result.

The AI should:

1. Read this guide and the repository-level `AGENTS.md`.
2. Inspect the target without changing it.
3. Identify existing Git roots, tracked or ignored nested repositories, project instructions, `docs/ai/` in ancestors and relevant children, submodules, working-tree changes, and the actual product boundary.
4. Reuse a covering layer or recommend one initialization root for the product, and explain where shared and repository-specific facts should live. Do not initialize each child simply because it has its own Git root.
5. Explain the generated files, current limitations, and rollback path, along with the owning Git repository and tracking scope. Reuse the root's existing Git repository; if absent, include its creation explicitly in the adoption plan.
6. Run a dry-run.
7. Ask the user only when the target, authority boundary, overwrite behavior, or Git organization requires a real choice. A user's explicit request for a parent Git repository authorizes that part of the confirmed plan; do not ask for the same authorization again.
8. Establish the authorized owning Git repository if needed, initialize after the scope is clear, validate the files and tracking boundary, and explain daily use. Report any pending commit separately; creating files or running `git init` alone does not produce a recorded version.

The AI may decide safe and reversible details from inspected evidence. It must not silently restructure Git repositories, overwrite existing instructions, write machine-specific paths into committed files, or enable optional capabilities.

## Manual setup

Clone the kit and enter its directory:

```powershell
git clone https://github.com/gaogushenling/ai-project-os.git
cd ai-project-os
```

Run the commands below from the kit checkout, with `--target` pointing to the confirmed collaboration root. If working elsewhere, use the resolved script and target paths; initialization does not copy these maintenance scripts into the target. Preview all planned files before writing:

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

Initialize after reviewing the preview:

```powershell
python scripts/init_project_os.py --target <project-root>
```

The initializer preserves existing files by default. Do not use `--force` until you have reviewed which template and protocol files it refreshes. It also refuses to create a layer below an existing ancestor layer, even with `--force` or `--dry-run`. Use `--allow-nested` only when an independent nested project deliberately needs its own layer; it does not consolidate existing layers.

## Choose the project root

### Single repository

For a standalone product in one repository, use its Git repository root as `<project-root>`. If it already belongs to a product workspace with a shared layer, reuse that layer instead. The generated files can be committed with their owning repository.

### Multi-repository workspace

For several repositories belonging to one product under a common parent, prefer one layer at that parent, with its own Git repository to version shared records. The collaboration root is the product/context boundary; child Git repositories retain their code and independent histories. Reuse an existing parent Git repository, or include creating one in an explicitly authorized adoption plan. Do not choose an unrelated collection of projects as one workspace merely to reduce file count.

For example, initialize only `product-workspace/`:

```text
product-workspace/
  .git/                       # shared records and selected workspace documents
  .gitignore                  # excludes complete child repository directories
  AGENTS.md
  .agents/skills/project-memory/SKILL.md
  docs/ai/                     # one shared layer
  api/.git/                    # independent code repository
  web/.git/                    # independent code repository
```

Keep ownership and execution explicit:

- Shared identity, repository roles, cross-repository decisions, memory, and acceptance rules live in the parent layer. In `docs/ai/project.json`, give the parent `{"path": ".", "role": "workspace-control"}` and add children such as `{"path": "api", "role": "backend"}` and `{"path": "web", "role": "frontend"}`. Use verified roles rather than leaving the template's `.` labeled as the primary code repository.
- Repository-specific facts can live in optional `docs/ai/repositories/api.json` and `web.json`, loaded only by matching routes. Existing native instructions, README files, and code stay in their repositories; route to them rather than copying their contents.
- Every repository command declares a workspace-relative working directory: for example, `{"command": "npm test", "cwd": "web"}`. Do not run a child's command in the parent or assume all repositories share tools and verification status. This is an example, not a verified command.
- Git status, diff, commit, and history checks run in the owning repository: shared records in the parent, code in each child. The parent Git repository does not automatically pin child revisions or combine their histories.
- Portable paths are relative to the collaboration root. Machine-specific checkout mappings remain local-only, and routes cannot escape the root, including through symlinks.

Open the AI at the parent workspace for daily use. Parent-only files are not guaranteed to be discovered by a session started at a child Git root. Codex, for example, normally searches project instructions and skills only within its detected project/Git scope ([AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skill discovery](https://learn.chatgpt.com/docs/build-skills)). If child-only sessions are required, explicitly load the parent `AGENTS.md` and memory entry, or deliberately add a thin relative pointer that preserves native child rules. A pointer is not another initialization, and it does not make parent MCP configuration automatically available. Verify configuration discovery and trust in the chosen tool separately.

If the parent has no Git repository yet, treat generated files as preparation, and establish the authorized parent Git repository before declaring complete adoption. The initializer does not do this for you. Do not move checkouts or convert them to submodules as a side effect. For unrelated products or intentionally standalone projects, separate initialization remains appropriate.

### Version the shared workspace safely

The default parent tracking scope is the shared AI layer, its ignore rules, and workspace documents the user has selected. Exclude complete independent child repositories with root-anchored ignore entries. The parent still reads their files through routes, while each child owns its code history.

Before writing, verify the chosen product boundary and the actual repository roots. These read-only commands are examples for children named `api` and `web`; use inspected names:

```powershell
git -C <project-root> rev-parse --show-toplevel
git -C <project-root> status --short
git -C <project-root> ls-files --stage
git -C <project-root> ls-files --stage -- api web
git -C <project-root>/api rev-parse --show-toplevel
git -C <project-root>/api status --short
git -C <project-root>/web rev-parse --show-toplevel
git -C <project-root>/web status --short
```

If the parent has no Git repository, its Git checks may fail; if they resolve to an ancestor, that ancestor is not a Git repository owned by the selected root. If an existing parent already tracks child files or has `160000` gitlink entries, record that evidence and resolve the tracking/topology choice before changing its index. Ignore rules do not untrack existing entries. Deliberately chosen existing submodules keep their authorized topology; do not remove their gitlinks to satisfy the independent-child example below.

Run the initializer's dry-run from the kit checkout as shown above. Only after the scope and parent-Git plan are confirmed, create Git when the root does not already own a repository:

```powershell
git -C <project-root> init
```

Then run the initializer from the kit checkout, complete the verified facts, and add these entries to the parent's `.gitignore`, preserving its existing rules. Substitute actual child directory names and inspect any later rules that could override these exclusions:

```gitignore
/api/
/web/
```

Review the full file inventory, including untracked files and logs, and keep private materials and local checkout mappings excluded. Before staging, confirm the child directories are ignored. Stage only the reviewed shared-layer paths and ignore file; add selected workspace documents by exact path in a separate command:

```powershell
git -C <project-root> check-ignore -- api/ web/
git -C <project-root> add -- .gitignore AGENTS.md .agents/skills/project-memory/SKILL.md docs/ai
git -C <project-root> diff --cached --name-status
git -C <project-root> diff --cached
git -C <project-root> ls-files --stage
git -C <project-root> ls-files --stage -- api web
```

Do not use `git add .` or force-add child directories. For this independent-child layout, the final parent index must contain neither `160000` gitlinks nor child code; the last command must have no output. Review all staged content before committing. When the user requests recording the collaboration layer in parent Git, a reviewed local commit within the confirmed scope is already authorized; follow the project's commit process without asking again. Remote creation/configuration and pushing require their own authorization. For example, after review:

```powershell
git -C <project-root> commit -m "Initialize shared AI collaboration layer"
git -C <project-root> show --stat --oneline HEAD
git -C <project-root> status --short
```

Check that the local commit contains only the intended shared records. If Git identity is missing or project rules prevent a commit, report "version recording pending"; do not change global identity or treat `git init` as history. Complete adoption still awaits the recorded version.

Parent Git versions shared facts; it does not make a parent clone reproduce child repositories or lock their revisions. If revision pinning is required, let the user choose an explicit manifest or submodule workflow. Do not change repository structure automatically.

### Git submodules

Submodules are useful when a parent repository must pin and reproduce exact child revisions. They add operational cost: cloning, branch switching, updates, CI, and detached-HEAD behavior need deliberate handling.

AI Project OS may describe an existing submodule layout, but it must not convert repositories into submodules without an explicit user request.

### Ignored nested repositories

Ignored nested repositories are the default for a shared parent Git repository whose children retain independent histories. The parent versions the collaboration layer and selected workspace documents. It does not automatically record child remotes or revisions, so a fresh parent clone cannot reproduce the complete workspace by itself.

Use this as a local organization choice, not as evidence that the parent owns or versions the child repositories. Record only portable logical roles in committed files and keep local checkout mappings ignored.

Independent sibling repositories outside the initialized root remain outside the current route-safety boundary. For one product, choose a suitable common parent before initializing, if its scope is authorized. Otherwise keep only logical relationships or use separate layers. Do not add out-of-root route targets.

### Consolidate existing child layers

Parent initialization preserves existing files and does not automatically migrate or remove child layers. Before consolidating:

1. Inventory and back up every child layer, its instruction changes, capability manifest/lock, and ignore-rule additions from the current files. Check each child working tree and index; untracked or uncommitted files can still contain valuable verified facts. A copy of `HEAD` alone is not a backup of this state.
2. Run a dry-run for the confirmed parent, establish its authorized Git repository and child exclusions, then initialize. Reconcile shared facts once; preserve repository-specific facts, sources, verification dates, and memory with explicit repository attribution.
3. Rebase file references and command working directories to the parent. An old `cwd: "."` becomes the owning child's relative path; inspect structured paths rather than blindly replacing text. Resolve conflicting instructions and duplicate capability IDs or differing locked versions before choosing one shared configuration.
4. Validate the parent layer and exercise relevant routes and command directories. Verify how the AI loads the parent entry in real use. Layer validation does not verify business builds or tool connections.
5. Only after migration and removal scope are authorized, remove confirmed redundant layer files and obsolete instruction sections. Preserve native child rules and unrelated `docs/`, skills, configuration, and ignore entries. A thin pointer may remain if child-only sessions need it.

Keep the backup until the consolidated layer is accepted. To roll back, restore only the changed layer files and instruction/ignore additions from the inventory; do not reset child repositories or rewrite history.

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

Review the owning Git repository's staged diff and tracking boundary. Commit only the reviewed shared-layer files and selected workspace documents when committing is authorized. Report missing Git ownership or a pending first commit explicitly; file preparation and file validation alone do not establish version history.

## Daily use

Start the AI at the collaboration root (the parent for a shared workspace) and describe the task normally. Once the entry is loaded, the project protocol automatically applies through compatible agents: they read `AGENTS.md`, enter project memory, and route the request. A child-only session may need explicit parent loading as described above. For example:

> Investigate this request. Load only the relevant project facts, define the smallest complete outcome, and state the verification evidence before delivery.

During work, the AI should:

1. Read the project `AGENTS.md`.
2. Enter through `.agents/skills/project-memory/SKILL.md`.
3. Match the task in `docs/ai/routes.json` and load only the listed files.
4. Use commands and boundaries recorded in `docs/ai/project.json` and routed repository facts; resolve file paths from the collaboration root and execute commands in their declared working directories.
5. Record only failures or corrections that will change later execution.
6. Separate implementation, engineering verification, and product acceptance in its final report.

Update project facts when the project changes. Do not use project memory as a conversation transcript or general documentation dump.

## Updating an initialized project

Pull or download a newer AI Project OS version, run `--dry-run` against the initialized project, and review the proposed additions. A normal re-run preserves existing files and filled state. `--force` refreshes template and protocol files but still protects the filled state files under `docs/ai/`; merge intentional local changes carefully.

Always validate after an update. Installed third-party skills and managed MCP blocks are checked against their lock hashes.

## Rollback and removal

There is no automatic uninstall command because initialization may preserve or coexist with project files that were already present. Use the owning Git repository's evidence and the pre-adoption inventory/current-file backup to remove only what adoption actually changed. If only non-Git file preparation was performed, use that inventory and backup; it was not complete adoption:

1. Review `git status`, staged and unstaged diffs, and untracked files before removing anything. Preserve pre-existing uncommitted facts; restoring `HEAD` does not restore those facts.
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
- Creating parent Git and recording reviewed local versions must be within the authorized scope. A user's request to record the collaboration layer in parent Git covers those steps; remote setup, pushes, submodule conversion, and tracking additional documents require their own authorization.

## Troubleshooting

### The dry-run reports existing files

Review the existing content and decide whether to keep it, merge the AI Project OS contract manually, or use `--force` for the refreshable templates. Do not overwrite project instructions blindly.

### Strict validation reports placeholders

Fill the reported fields with verified project facts. If a value is genuinely unknown, keep normal validation and report the unfilled item instead of inventing an answer.

### A route target is outside the project

For repositories in one product, choose their common parent as the collaboration root before initialization. Otherwise move the portable fact inside the current root, use a separate layer, or document only the logical relationship. Do not bypass the route-safety check with absolute paths or symlinks.

### The initializer finds an ancestor layer

Use that root as `--target` to update or validate the shared layer, and route to the child as needed. `--force` is not a scope override. If the nested folder is a deliberately independent product, choose its separate scope explicitly before using `--allow-nested`.

### The AI does not automatically invoke the skill

Ask it to read the project `AGENTS.md` and `.agents/skills/project-memory/SKILL.md`, or explicitly say `Use $ai-project-os`. Tool support varies, but the committed project facts remain readable by any AI with file access.

### A capability cannot connect

Check the project capability manifest, local command availability, and required environment-variable names. Never paste secret values into `docs/ai/` or a prompt merely to make a connection work.

## Adoption checklist

- The initialization root and fact owner are explicit.
- The collaboration root owns a Git repository; intended shared records have recorded versions, or the pending first commit is clearly reported.
- The parent tracking scope is verified. In the default independent-child layout, child directories are ignored and its index contains neither child code nor `160000` gitlinks.
- Existing instructions were preserved or intentionally reconciled.
- Normal validation passes; strict validation is used when placeholders are complete.
- Commands and quality gates were verified rather than guessed.
- Multi-repository roles are logical and portable.
- No committed file contains secrets or absolute local paths.
- The user knows how to invoke AI Project OS and where future facts belong.
