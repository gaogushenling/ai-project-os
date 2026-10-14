---
name: project-memory
description: Load the minimum verified project or workspace facts, routes, capabilities, and operational memory needed for the current task.
---

# Project Memory

Load order only — the facts themselves live in `docs/ai` at the collaboration root, three directories above this skill directory. Resolve all memory and route paths from that root rather than the current shell directory. Child repositories reuse this entry; repository-specific facts load through routes.

1. Match the request against `docs/ai/routes.json`.
2. Read only the files listed by the best matching route.
3. Read `docs/ai/capabilities.json` before choosing an optional Skill or MCP Server.
4. Use only capabilities enabled for this project; installation alone is not execution authorization.
5. For commands and quality gates, use `docs/ai/project.json` and the routed repository facts. Run each command in its declared repository working directory; preserve applicable child instructions and Git boundaries.
6. For a relevant known failure, correction, or regression, use `docs/ai/memory.json`.
7. Update memory only with verified, reusable evidence.
8. When facts conflict, use git history in each document's owning repository (`git log -1 --format=%cs -- <repo-relative-path>`) and `verified_at` for memory entries; non-Git files need verified source dates or an explicit unknown. Check older constraints dropped during a change and record confirmed resolutions with `verified_at`.
9. Review related memory after the code, tests, or approach it depends on changes; entries past `expires_at` must be re-verified or removed, not reused.

Never store secrets or machine-private values in committed project memory. Project MCP configuration may reference environment variable names, but must not contain their values.
