---
name: project-memory
description: Load the minimum verified project facts, routes, capabilities, and operational memory needed for the current repository task.
---

# Project Memory

Load order only — the facts themselves live in `docs/ai`.

1. Match the request against `docs/ai/routes.json`.
2. Read only the files listed by the best matching route.
3. Read `docs/ai/capabilities.json` before choosing an optional Skill or MCP Server.
4. Use only capabilities enabled for this project; installation alone is not execution authorization.
5. For commands and quality gates, use `docs/ai/project.json`.
6. For a relevant known failure, correction, or regression, use `docs/ai/memory.json`.
7. Update memory only with verified, reusable evidence.
8. When facts conflict, prefer the more recent verified source — use git history for documents (`git log -1 --format=%cs -- <path>`) and `verified_at` for memory entries; check the older source for still-valid constraints dropped during a change, and record confirmed resolutions with `verified_at`.
9. Review related memory after the code, tests, or approach it depends on changes; entries past `expires_at` must be re-verified or removed, not reused.

Never store secrets or machine-private values in committed project memory. Project MCP configuration may reference environment variable names, but must not contain their values.
