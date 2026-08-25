# AI Project OS Repository Instructions

These instructions apply when an AI receives this repository to explain, recommend, or perform adoption in another project.

## Start here

- Read `README.md` and `docs/getting-started.md`; use `README_zh.md` and `docs/getting-started_zh.md` when the user prefers Chinese.
- Treat this repository as a portable adoption kit. Keep its reusable instructions free of project-specific names, private URLs, machine-specific paths, credentials, and historical facts.
- If the user only asks a question or requests a recommendation, do not modify their project.

## Adoption workflow

1. First inspect the target read-only: existing Git roots, submodules, ignored nested repositories, project instructions, `docs/ai/`, working-tree state, and relevant commands.
2. Distinguish a single repository from a multi-repository workspace. Identify which repository should own shared facts and which repositories own code-specific facts.
3. Recommend the smallest suitable adoption mode and explain why, what files it creates, what remains local, what is not supported, and how to rollback or remove the layer.
4. Decide safe, reversible details from evidence. If the target, authority boundary, Git topology, overwrite behavior, or another material choice is ambiguous, ask the user before writing.
5. Run `scripts/init_project_os.py --target <project-root> --dry-run` before initialization. Apply only within the confirmed target, then validate the generated layer.
6. Report implemented, verified, unverified, and user-decision items separately.

## Safety boundaries

- Do not convert repositories to Git submodules, move repositories, create a parent repository, rewrite Git history, or overwrite existing instructions unless the user explicitly requests that change.
- Do not install optional capabilities, enable MCP servers, perform external writes, or change production systems merely because they are available.
- Do not put absolute local paths, secrets, private endpoints, or environment-specific failures in portable files. Keep local-only facts in ignored project files.
- Do not claim that routes outside the initialized project root are supported; the current validator rejects them.

The complete human and AI usage contract is in [docs/getting-started.md](./docs/getting-started.md) and [docs/getting-started_zh.md](./docs/getting-started_zh.md).
