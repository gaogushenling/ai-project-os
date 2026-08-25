# Recommended public-source Skill projects and MCP Servers

**English** | [中文](./recommended-integrations_zh.md)

This catalog only recommends: recommendations are never installed or enabled automatically, and never replace the user's choice. After an explicit user choice, installation defaults to project scope. The machine-readable facts live in `recommended-integrations.json`.

Project-level conventions: third-party skills go into the project's declared `skill_directory` (the collaboration layer's own entry stays fixed at `.agents/skills/project-memory`), and MCP configuration goes into the project's declared `mcp_config` path (template defaults `.agents/skills` and `.codex/config.toml`; other tools change their own pointers in `docs/ai/capabilities.json`). Choices and revisions are recorded in `docs/ai/capabilities.json` and `docs/ai/capabilities.lock.json` respectively. Global installation requires an explicit user choice.

## Admission

- **Skill projects**: provide workflows, prompts, and best practices — they tell an agent how to do a class of work.
- **MCP Servers**: provide callable tool capabilities — they let an agent access browsers, code platforms, observability systems, or databases.
- **One recommendation per source repository**: the repository's highlighted capabilities are written into the same recommendation, without duplicating repository, maintainer, and license metadata.

The catalog lists projects with public source, explicit licenses, identifiable maintainers, and inspectable implementations. License kinds:

- **Open Source**: uses an OSI open-source license.
- **Source-Available**: source is viewable, but use, competitive use, or redistribution may be restricted; not the same as open source.

Always re-verify the current version's source, license, and terms before installation. Large skill collections install only the selected child skill, never the whole repository.

## Recommendation tiers

- **Baseline**: broadly useful and safe to show by default, but the user still decides whether to install.
- **Scenario**: shown only when the user's goal or project evidence matches.
- **Production-risk**: involves credentials, external writes, or production environments; shown only when the user states the corresponding goal, with confirmation again before execution.

The same repository may contain capabilities of different tiers; judge by the capability actually used. Installing a repository grants no external-write or production-operation authorization.

## Skill projects

| Project | Tier | Highlighted capabilities | Recommended when | Repository | License kind | License |
| --- | --- | --- | --- | --- | --- | --- |
| Superpowers | Baseline / Scenario | Verification before completion, debugging, TDD, planning, code review, worktrees, branch finishing | An engineering workflow covering the full development process | [obra/superpowers](https://github.com/obra/superpowers) | Open Source | [MIT](https://github.com/obra/superpowers/blob/main/LICENSE) |
| Terminal Skills | Scenario | Docker Helper, SQL Optimizer | Container configuration and troubleshooting, or evidenced SQL performance issues | [TerminalSkills/skills](https://github.com/TerminalSkills/skills) | Open Source | [Apache-2.0](https://github.com/TerminalSkills/skills/blob/main/LICENSE) |
| UI/UX Pro Max | Scenario | UI/UX Pro Max | New interfaces, visual direction, design systems, or multi-stack UI guidance | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Open Source | [MIT](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/LICENSE) |
| OpenSpec | Scenario | Spec-driven development: proposal, implementation, verification | Explicit OpenSpec adoption, or an existing OpenSpec workspace | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | Open Source | [MIT](https://github.com/Fission-AI/OpenSpec/blob/main/LICENSE) |
| Vercel Agent Skills | Scenario / Production-risk | React Best Practices, Web Design Guidelines, Deploy to Vercel | React / Next.js development, web review, or Vercel deployment | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | Open Source | [MIT](https://github.com/vercel-labs/agent-skills#license) |
| Cloudflare Skills | Scenario / Production-risk | Web Performance, Wrangler | Web performance diagnosis or Cloudflare Workers | [cloudflare/skills](https://github.com/cloudflare/skills) | Open Source | [Apache-2.0](https://github.com/cloudflare/skills/blob/main/LICENSE) |
| Awesome GitHub Copilot | Scenario / Production-risk | Codebase understanding, refactoring plans, spec extraction, Harness Engineering, high-risk operation verification | Explicit selection of one checked development-quality skill | [github/awesome-copilot](https://github.com/github/awesome-copilot) | Open Source | [MIT](https://github.com/github/awesome-copilot/blob/main/LICENSE) |
| Agent Skill Eval | Scenario | Skill security auditing, capability evaluation, trigger testing, version regression, token cost | Installing, upgrading, comparing, or developing third-party skills | [aws-samples/sample-agent-skill-eval](https://github.com/aws-samples/sample-agent-skill-eval) | Open Source | [MIT-0](https://github.com/aws-samples/sample-agent-skill-eval/blob/main/LICENSE) |
| Sentry Agent Skills | Scenario / Production-risk | SDK onboarding, Sentry issue fixing, PR issue handling | Projects already using Sentry | [getsentry/sentry-agent-skills](https://github.com/getsentry/sentry-agent-skills) | Open Source | [Apache-2.0](https://github.com/getsentry/sentry-agent-skills#license) |
| Microsoft Skills | Scenario | Microsoft SDK, Azure, Foundry, MCP Builder | Microsoft stacks or MCP Server development | [microsoft/skills](https://github.com/microsoft/skills) | Open Source | [MIT](https://github.com/microsoft/skills/blob/main/LICENSE) |
| Agent Toolkit for AWS | Scenario | AWS architecture, SDK, IaC, observability, security, DevSecOps | Projects built on or running in AWS | [aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) | Open Source | [Apache-2.0](https://github.com/aws/agent-toolkit-for-aws/blob/main/LICENSE) |

"Highlighted capabilities" only explains the recommendation; it is not the repository's full content. Large community collections must first select and inspect the specific skill — never enable the whole repository unconditionally.

## MCP Servers

| Project | Tier | Recommended when | Repository | License kind | License |
| --- | --- | --- | --- | --- | --- |
| Playwright MCP | Scenario | Web projects needing real browser actions, screenshots, or end-to-end acceptance | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Open Source | [Apache-2.0](https://github.com/microsoft/playwright-mcp/blob/main/LICENSE) |
| GitHub MCP Server | Scenario | GitHub Issue, PR, review, or Actions collaboration | [github/github-mcp-server](https://github.com/github/github-mcp-server) | Open Source | [MIT](https://github.com/github/github-mcp-server/blob/main/LICENSE) |
| CodeGraph | Scenario | Cross-file call chains, impact analysis, architecture understanding, or repeated code search | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | Open Source | [MIT](https://github.com/colbymchenry/codegraph/blob/main/LICENSE) |
| Semgrep MCP Server | Scenario | Deterministic checks for code defects, security issues, sensitive information, and project rules | [semgrep/semgrep](https://github.com/semgrep/semgrep) | Open Source | [LGPL-2.1](https://github.com/semgrep/semgrep/blob/develop/LICENSE) |
| Context7 | Scenario | Current-version third-party library docs and code examples | [upstash/context7](https://github.com/upstash/context7) | Open Source | [MIT](https://github.com/upstash/context7/blob/master/LICENSE) |
| Grafana MCP | Production-risk | Production evidence from metrics, logs, traces, alerts, and events | [grafana/mcp-grafana](https://github.com/grafana/mcp-grafana) | Open Source | [Apache-2.0](https://github.com/grafana/mcp-grafana/blob/main/LICENSE) |
| SonarQube MCP Server | Scenario | SonarQube code quality, security issues, and Quality Gate | [SonarSource/sonarqube-mcp-server](https://github.com/SonarSource/sonarqube-mcp-server) | Source-Available | [Sonar-Source-Available-1.0](https://github.com/SonarSource/sonarqube-mcp-server/blob/master/LICENSE) |
| Sentry MCP Server | Production-risk | Query Sentry issues, traces, releases, and project data | [getsentry/sentry-mcp](https://github.com/getsentry/sentry-mcp) | Source-Available | [FSL-1.1-Apache-2.0](https://github.com/getsentry/sentry-mcp/blob/main/LICENSE.md) |
| DBHub | Production-risk | Controlled queries against PostgreSQL, MySQL, MariaDB, SQL Server, or SQLite | [bytebase/dbhub](https://github.com/bytebase/dbhub) | Open Source | [MIT](https://github.com/bytebase/dbhub/blob/main/LICENSE) |

Source-Available license notes:

- SonarQube MCP currently licenses non-competitive use; it is not an OSI open-source license.
- Sentry MCP currently uses FSL-1.1; each release converts to Apache-2.0 two years after release.

High-risk operation requirements:

- Grafana, SonarQube, and Sentry start with read-only, least-privilege credentials by default; external writes require separate confirmation.
- DBHub must use a database-level read-only account; the MCP's own SQL read-only check is not a security boundary. Configure row limits and query timeouts, and re-check its [SQL Server read-only bypass issue](https://github.com/bytebase/dbhub/issues/349) before use.
- Context7 accesses a hosted documentation service; queries must not carry secrets, proprietary source, or sensitive business data.

## Usage rules

1. Start from the user's current goal, then project evidence; an explicit user choice wins.
2. Recommend and install only the minimum capability that closes the current scenario; do not install or enable everything just because the repository contains a lot.
3. Before installation, re-check the repository, the current license, maintenance status, and the specific skill or MCP content.
4. Source-Available projects must confirm the intended use complies with the license restrictions, and be accepted explicitly by exact license name at installation.
5. Default to project-level installation; global installation is only for personal capabilities that genuinely need to apply across all projects.
6. For credentials, external writes, production reads, or database operations, installation does not authorize execution — confirm explicitly before running.
