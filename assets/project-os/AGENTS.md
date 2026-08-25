# AI collaboration

This repository uses a small project-local collaboration layer.

## Start here

1. Read `.agents/skills/project-memory/SKILL.md`.
2. Match the request in `docs/ai/routes.json`.
3. Load only the files listed by that route.
4. Use `docs/ai/project.json` for verified project facts and commands.
5. Use `docs/ai/memory.json` only for relevant failures, corrections, and regressions.
6. Before using an optional Skill or MCP Server, check `docs/ai/capabilities.json` and use only project-enabled capabilities.

Current user instructions, executable code, tests, and project-native rules override recorded memory when they conflict.

## Working agreement

- Keep project memory concise, evidence-based, and free of secrets.
- When sources conflict, check recency with git first (`git log -1 --format=%cs -- <path>`): prefer the newer source for the current approach, then review the older source for still-valid constraints dropped during the switch. Untracked or locally modified files count as newest. Record confirmed conflicts and their resolutions in project memory.
- Review recorded failures and corrections after the code or tests they depend on change; re-verify or remove entries past `expires_at` instead of reusing them.
- Keep capability declarations and locks project-scoped; never commit credential values.
- Start non-trivial work from the user-visible outcome and real constraints, not from available technology or a generic checklist.
- Define the user, current flow, target flow, smallest complete scope, important failure paths, and acceptance evidence before implementation.
- Check UI, API, backend, data, transactions, idempotency, concurrency, indexes, performance, permissions, audit, and observability only when relevant to the outcome or a material risk.
- Classify adjacent issues as a blocker, required risk, or later improvement. Implement only blockers and required risks; record later improvements without expanding the task.
- Communicate the conclusion first, in plain language, with only the detail the reader needs to decide, implement, or verify.
- Run the project-native checks recorded in `docs/ai/project.json` before claiming verification.
- Ask before production changes, destructive data operations, credential handling, or other actions marked for confirmation.
- Record a failure or correction only when it changes future decisions.
- At delivery, separate implementation, engineering verification, and product acceptance; do not claim a higher level without evidence.
