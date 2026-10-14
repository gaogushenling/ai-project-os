# AI Project OS Repository Instructions

These instructions apply when an AI receives this repository to explain, recommend, or perform adoption in another project.

## Start here

- Read `README.md` and `docs/getting-started.md`; use `README_zh.md` and `docs/getting-started_zh.md` when the user prefers Chinese.
- Treat this repository as a portable adoption kit. Keep its reusable instructions free of project-specific names, private URLs, machine-specific paths, credentials, and historical facts.
- If the user only asks a question or requests a recommendation, do not modify their project.

## Adoption workflow

1. First inspect the target read-only: existing Git roots, submodules, ignored nested repositories, project instructions, `docs/ai/` in the target, ancestors and relevant children, working-tree state, and relevant commands.
2. Distinguish the product/workspace boundary from code repository boundaries. For repositories belonging to one product under a common parent, prefer one collaboration layer versioned in that parent's own Git repository. Reuse an existing parent repository; if none exists, include establishing it in the adoption plan. Do not select a broad folder containing unrelated products.
3. Reuse an existing layer that covers the intended scope; do not initialize each child merely because it has its own Git root. Keep shared facts at the collaboration root and route to repository-specific facts and native documents. Recommend the smallest suitable adoption mode and explain why, what files it creates, what remains local, what is not supported, and how to rollback or remove the layer.
4. Decide safe, reversible details from evidence. If the target, authority boundary, Git topology, overwrite behavior, or another material choice is ambiguous, ask the user before writing.
5. Run `scripts/init_project_os.py --target <project-root> --dry-run` before initialization. Apply only within the confirmed target, then validate the generated layer, its own Git root, and version history. File generation or an empty Git repository is preparation, not completed version recording. Review and record the layer according to the project workflow; report any uncommitted records as pending. If the user already requested a parent Git repository, proceed within that confirmed scope without asking for the same authorization again.
6. Report implemented, verified, unverified, and user-decision items separately.

## Safety boundaries

- Do not convert repositories to Git submodules, move repositories, create a parent repository, rewrite Git history, or overwrite existing instructions unless the user explicitly requests that change.
- Do not install optional capabilities, enable MCP servers, perform external writes, or change production systems merely because they are available.
- Do not put absolute local paths, secrets, private endpoints, or environment-specific failures in portable files. Keep local-only facts in ignored project files.
- Do not claim that routes outside the initialized project root are supported; the current validator rejects them.
- A parent layer does not version child repositories or guarantee automatic discovery when an AI starts at a child Git root. Prefer opening the parent workspace; use explicit loading or a deliberately chosen thin pointer for child-only sessions, not a second full layer.
- For independent nested repositories, keep their directories out of the parent's index using root-anchored ignore entries. Inspect already tracked paths first; ignores do not untrack existing content. Stage only confirmed collaboration files, never capture child code or accidental Git links with a broad add. A remote or push requires its own requested scope.
- Existing child layers require evidence-preserving consolidation before removal. Never discard their facts, memories, capabilities, or native instructions as a side effect of parent initialization.

The complete human and AI usage contract is in [docs/getting-started.md](./docs/getting-started.md) and [docs/getting-started_zh.md](./docs/getting-started_zh.md).
