# AI Project OS

**English** | [中文](./README_zh.md)

A lightweight, portable project-level AI collaboration layer. Project rules, skills, MCP configuration, and capability versions live with the project by default, with no dependence on a developer machine's global configuration.

## Motivation and purpose

AI-assisted development is evolving from the use of a single tool into a personal workbench. Each developer combines different models, IDEs, Skills, MCP servers, automation tools, and working habits. The projects, environments, and problems they encounter also vary widely. Personal AI development is naturally diverse and should not be forced into one standardized workflow.

Despite those differences, several foundational problems remain: how an AI understands the current project, loads only the context required for a task, retains useful failures and corrections, manages adopted capabilities and their risk boundaries, and verifies delivery with evidence.

AI Project OS exists to provide a lightweight, portable, project-level foundation for personal AI development workbenches. This foundation takes the form of a project-level collaboration layer: it keeps project facts, context routing, useful memory, capability state, risk boundaries, and delivery validation with the project itself, allowing different AI tools, IDEs, and environments to continue working from the same trusted information.

It does not prescribe one model, toolchain, or development methodology, nor does it try to make every personal workbench identical. It provides a minimal common foundation on which each developer can assemble their own AI development platform while keeping project knowledge durable, collaboration seamless across tools and sessions, capability state traceable, and delivery verifiable.

It does not replace project documentation, development methodology, or human decision-making. It solves exactly five problems:

- Keeping project facts in the project instead of writing them into global skills
- Loading context on demand, according to the task
- Recording the tool failures and user corrections that will actually change the next execution
- Keeping an explicit confirmation boundary for high-risk operations
- Verifying with executable checks that the collaboration layer has not broken

The generated `AGENTS.md` follows the project-level instruction file convention introduced by OpenAI Codex ([official docs](https://developers.openai.com/codex/agents-md)) and [supported by GitHub Copilot](https://github.blog/changelog/2026-06-23-copilot-coding-agent-now-supports-agents-md-custom-instructions/): the instruction file lives at the repository root. This collaboration layer extends it with routing, memory, capability manifests, and executable validation. Instructions are layered by scope: `AGENTS.md` → `.agents/skills/project-memory` → `docs/ai/`.

## First principles

> Let any AI enter a project and, based on the project's own verified information, keep delivering usable, verifiable, reproducible results with the minimum necessary capabilities — without overstepping.

1. **The project is the source of truth**: rules, context, skills, MCP configuration, and versions live with the project, not in a personal global environment.
2. **The goal is product delivery**: the measure is whether users can use the result and whether it can be accepted — not how much code was generated.
3. **Only the minimum necessary capabilities**: load, install, and enable only what the current project actually needs.
4. **Evidence over claims**: distinguish implementation, engineering verification, and product acceptance; never raise the completion level without evidence.
5. **Capability is not permission**: recommended ≠ installed, installed ≠ enabled, enabled ≠ authorized to run production operations.
6. **AI is bound by the project**: never expand scope, modify production, handle secrets, or make high-risk decisions on the user's behalf.

It must not become: a comprehensive skill store, a methodology encyclopedia, another heavy development framework, a scaffold that installs every tool, or a replacement for the project's own documentation and engineering standards.

There is only one question for adding a feature: does it help AI understand the project more accurately, complete real tasks more reliably, or make delivery easier to verify? If it does none of the three, it does not go in.

## Product development protocol

- Start from the outcome the user actually wants, then decide on the technical approach.
- Deliver the smallest complete business loop first; check risks by actual impact instead of mechanically stacking design.
- Classify adjacent issues as current blocker, required risk, or later improvement, so tasks do not grow without limit.
- When documentation or code conflicts, check recency first: use git to find each side's last change (`git log -1 --format=%cs -- <path>`); the newer document usually represents the current approach, and constraints, boundaries, and notes dropped from the older document during a switch must be reviewed and restored rather than treated as a contradiction.
- Lead with the conclusion, use plain language, and separate implementation, engineering verification, and product acceptance.

## What initialization generates

```text
AGENTS.md
.agents/skills/project-memory/SKILL.md
docs/ai/capabilities.json
docs/ai/capabilities.lock.json
docs/ai/project.json
docs/ai/routes.json
docs/ai/memory.json
docs/ai/logs/YYYY-MM-DD.md
```

Only 8 core entry points. Structured data is standard JSON; the scripts depend only on the Python standard library and require Python 3.11+ (CI verifies 3.11–3.13).

## Optional capability recommendations

The repository ships a small, strict catalog of public-source recommendations: humans read `references/recommended-integrations.md`, programs read `references/recommended-integrations.json`.

- Skills are recommended by source repository; MCP Servers are maintained separately as tool projects; one recommendation per source repository.
- Only projects with verifiable public source, an explicit license, and an identifiable maintainer are listed, distinguishing Open Source from Source-Available.
- Baseline is visible by default, Scenario is recommended on user intent or project evidence, and Production-risk only for explicit external-service or production goals.
- Recommendations are never installed or enabled automatically; after an explicit user choice, the default is project-level installation or configuration, recorded in the project manifest and lock file.
- Large skill collections are never installed wholesale; only the selected child skill is copied, and global installation requires an explicit user choice.

List everything:

```powershell
python scripts/list_recommended_integrations.py
```

Filter by type, tier, or tag:

```powershell
python scripts/list_recommended_integrations.py --type skill-project --tier scenario
python scripts/list_recommended_integrations.py --type mcp-server --tag web --format json
python scripts/list_recommended_integrations.py --license-kind source-available
```

## Project-level installation

Third-party skills install by default into the `skill_directory` declared in the project's `docs/ai/capabilities.json` (template default `.agents/skills`); the collaboration layer's own project-memory entry stays fixed at `.agents/skills/project-memory` and does not follow the declaration. Large collections must name one skill:

```powershell
python scripts/install_project_integration.py --target <project-root> --id superpowers --skill systematic-debugging
```

MCP configuration is written to the `mcp_config` path declared in the project's `docs/ai/capabilities.json` (template default `.codex/config.toml`; point it at your tool's file when using another tool). Servers are disabled by default and enabled only with an explicit `--enable`. Secrets are recorded as environment variable names, never values:

```powershell
python scripts/install_project_integration.py --target <project-root> --id context7 --command npx --arg=-y --arg=@upstash/context7-mcp --env-var CONTEXT7_API_KEY
```

Installation results are recorded in:

- `docs/ai/capabilities.json`: what the project needs, plus install, enable, configure, and verify state.
- `docs/ai/capabilities.lock.json`: the concrete source, revision or configuration summary, and content checksums.

"Installed" is not "verified". MCP still requires local environment variables and an actual connection; production reads, external writes, and database operations still require separate authorization.

Source-Available projects also require `--accept-license <exact license name>` to confirm the current terms explicitly; the installer never treats "source visible" as unrestricted open source.

Legacy (Codex) projects still using `.codex/skills/project-memory` get the new `.agents/skills/project-memory`, capability manifest, and lock file added on re-initialization, without overwriting existing content. Remove the old copy yourself once the new path validates.

## Usage

### AI-guided adoption (recommended)

Give this repository and the target project to your AI, then say:

> Help me adopt AI Project OS in this project. Inspect it read-only first, recommend the right scope, show the dry-run result, and ask me only about decisions that materially change the result.

The repository-level `AGENTS.md` tells compatible coding agents how to inspect the target, choose between single- and multi-repository layouts, preserve existing rules, and stop for material user decisions. The complete human and AI workflow is in [Getting Started](./docs/getting-started.md).

### Manual quick start

Dry-run before writing:

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

Then initialize:

```powershell
python scripts/init_project_os.py --target <project-root>
```

Complete the verified project facts in `docs/ai/project.json`, review task routes in `docs/ai/routes.json`, and keep only behavior-changing failures or corrections in `docs/ai/memory.json`.

After initialization, start the AI in the project and state the task normally. Compatible agents automatically apply the project protocol; explicit `$ai-project-os` invocation is only a fallback when automatic instruction loading is unavailable.

Validate a target project:

```powershell
python scripts/validate_project_os.py --target <project-root>
```

Strict mode treats unfilled project placeholders as failures too:

```powershell
python scripts/validate_project_os.py --target <project-root> --strict
```

The validator also recomputes the lock file's content hashes — directory hashes of installed skills and hashes of managed MCP config blocks — and fails on content drift, warning when a lock entry lacks a hash field.

Run the complete self-check when maintaining this repository:

```powershell
python scripts/self_check.py
python -m unittest discover -s tests -v
```

## Design principles

- `SKILL.md` keeps only the cross-project protocol
- Project facts, commands, and boundaries belong to the project
- Existing files are not overwritten by default; `--force` only refreshes template and protocol files, and the filled state files under `docs/ai/` (project facts, memory, capability manifest, and lock) are never overwritten by the initializer — delete them manually to reset
- The default install scope is the project; global capabilities are only for personal preferences that genuinely apply across all repositories
- No dependence on a specific OS, IDE, model, or private tool path; the MCP config path and skill directory are declared by the project, with the template providing defaults only
- Never commit secrets, connection strings, or machine-private values

## Boundaries and limitations

- **The protocol relies on agent discipline**: route matching, progressive loading, and delivery gates are followed by the collaborating tool per its instructions; the validator only verifies the data itself (structure, paths, hashes, secrets) and cannot verify whether an agent actually worked by the protocol. Any enforcement mechanism would betray the minimum-necessary principle, so this is an honest declaration instead.
- **Secret detection is heuristic regex**: it covers the collaboration layer's own committed files and logs, may false-positive on legitimate examples shaped like `token = ...`, and does not replace a repository-wide dedicated secret scanner.
- **The recommendation catalog is hand-maintained static data**: licenses, URLs, and status age over time, so policy requires re-checking upstream before installation (the installer forces explicit license acceptance for Source-Available).

## Repository structure

```text
agents/       Codex display metadata (optional; affects Codex display only, ignored by other tools)
assets/       minimal templates initialized into target projects
scripts/      initialization, validation, and self-checks
tests/        behavior tests
```

Documentation is bilingual with English as the default; Chinese translations live alongside as `*_zh.md` files (`README_zh.md`, `SKILL_zh.md`, `references/recommended-integrations_zh.md`).

## Community

AI Project OS is shared with the open-source community on [LINUX DO](https://linux.do).

## Star History

<a href="https://www.star-history.com/?repos=gaogushenling%2Fai-project-os&type=date&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=gaogushenling/ai-project-os&type=date&theme=dark&legend=top-left&sealed_token=9G4fb-eCWzn_NBCAy8Fsu4BuRim5PbP1e6baTL7ZXxgMm0D1gE0MpzfAvLfhyb4CznPWPTlz0mxNjbHtD1NbKZx1jAgDSsdVXplkc6fMVxQdEumGVzIUKkyva1deGFKnXFoBPdjlparaS0HJlDEyp34dFOW-ElIMVW1fpfvTLT6pOebpkgMdOm5D5okV" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=gaogushenling/ai-project-os&type=date&legend=top-left&sealed_token=9G4fb-eCWzn_NBCAy8Fsu4BuRim5PbP1e6baTL7ZXxgMm0D1gE0MpzfAvLfhyb4CznPWPTlz0mxNjbHtD1NbKZx1jAgDSsdVXplkc6fMVxQdEumGVzIUKkyva1deGFKnXFoBPdjlparaS0HJlDEyp34dFOW-ElIMVW1fpfvTLT6pOebpkgMdOm5D5okV" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=gaogushenling/ai-project-os&type=date&legend=top-left&sealed_token=9G4fb-eCWzn_NBCAy8Fsu4BuRim5PbP1e6baTL7ZXxgMm0D1gE0MpzfAvLfhyb4CznPWPTlz0mxNjbHtD1NbKZx1jAgDSsdVXplkc6fMVxQdEumGVzIUKkyva1deGFKnXFoBPdjlparaS0HJlDEyp34dFOW-ElIMVW1fpfvTLT6pOebpkgMdOm5D5okV" />
  </picture>
</a>

## License

Apache-2.0
