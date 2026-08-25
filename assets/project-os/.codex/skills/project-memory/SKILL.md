---
name: project-memory
description: Load the minimum verified project facts, routes, and operational memory needed for the current repository task.
---

# Project Memory

This is the project-local entry point. Facts belong to `docs/ai`; this skill only defines how to load them.

1. Match the request against `docs/ai/routes.json`.
2. Read only the files listed by the best matching route.
3. For non-trivial work, satisfy the matched route's product gates without turning them into an exhaustive checklist.
4. For commands and quality gates, use `docs/ai/project.json`.
5. For a relevant known failure, correction, or regression, use `docs/ai/memory.json`.
6. Update memory only with verified, reusable evidence.

Never store secrets or machine-private values in committed project memory. Use ignored `.codex/local/` files when local-only notes are necessary.
