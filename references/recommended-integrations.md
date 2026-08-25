# 公开源码 Skill 项目与 MCP Server 推荐

这份清单只做推荐，不自动安装、不自动启用，也不代替用户选择。用户明确选择后，默认安装到项目级。机器可读的事实以 `recommended-integrations.json` 为准。

项目级约定：第三方 Skill 放入项目声明的 `skill_directory`（协作层自带入口固定在 `.agents/skills/project-memory`），MCP 配置写入项目声明的 `mcp_config` 路径（模板默认 `.agents/skills` 与 `.codex/config.toml`，其他工具在 `docs/ai/capabilities.json` 里改自己的指向即可）；选择结果和版本分别记录在 `docs/ai/capabilities.json` 与 `docs/ai/capabilities.lock.json`。全局安装必须由用户明确选择。

## 收录方式

- **Skill 项目**：提供工作流、提示词和最佳实践，告诉 Agent 怎样完成一类工作。
- **MCP Server**：提供可调用的工具能力，让 Agent 访问浏览器、代码平台、可观测系统或数据库。
- **一个源码仓库只保留一条推荐**：仓库里的重点能力写在同一条推荐中，不重复维护仓库、维护者和许可证。

清单收录公开源码、许可证明确、维护方可识别、实现可检查的项目。许可证分为：

- **Open Source**：使用 OSI 开源许可证。
- **Source-Available**：源码可查看，但用途、竞争性使用或再分发可能受限，不等于开源。

安装前必须重新核对当前版本的源码、许可证和使用条件。大型 Skill 集合只安装选中的子 Skill，不整仓启用。

## 推荐档位

- **Baseline**：通用价值高，可以默认展示，但仍由用户决定是否安装。
- **Scenario**：只在用户目标或项目证据命中时展示。
- **Production-risk**：涉及凭据、外部写入或生产环境，只在用户明确提出对应目标时展示，执行前再次确认。

同一仓库可能包含不同档位的能力，按实际要使用的能力判断。安装仓库不代表获得外部写入或生产操作授权。

## Skill 项目

| 项目 | 档位 | 重点能力 | 推荐场景 | 仓库 | 许可证类型 | License |
| --- | --- | --- | --- | --- | --- | --- |
| Superpowers | Baseline / Scenario | 验收前验证、调试、TDD、计划、代码审查、Worktree、分支收尾 | 覆盖开发全过程的工程工作流 | [obra/superpowers](https://github.com/obra/superpowers) | Open Source | [MIT](https://github.com/obra/superpowers/blob/main/LICENSE) |
| Terminal Skills | Scenario | Docker Helper、SQL Optimizer | 容器配置与排障，或有证据的 SQL 性能问题 | [TerminalSkills/skills](https://github.com/TerminalSkills/skills) | Open Source | [Apache-2.0](https://github.com/TerminalSkills/skills/blob/main/LICENSE) |
| UI/UX Pro Max | Scenario | UI/UX Pro Max | 新界面、视觉方向、设计系统或多技术栈 UI 指导 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Open Source | [MIT](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/LICENSE) |
| OpenSpec | Scenario | 提案、实施、验证等规格驱动开发流程 | 明确采用 OpenSpec，或项目已有 OpenSpec 工作区 | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | Open Source | [MIT](https://github.com/Fission-AI/OpenSpec/blob/main/LICENSE) |
| Vercel Agent Skills | Scenario / Production-risk | React Best Practices、Web Design Guidelines、Deploy to Vercel | React / Next.js 开发、Web 审查或 Vercel 部署 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | Open Source | [MIT](https://github.com/vercel-labs/agent-skills#license) |
| Cloudflare Skills | Scenario / Production-risk | Web Performance、Wrangler | Web 性能诊断或 Cloudflare Workers | [cloudflare/skills](https://github.com/cloudflare/skills) | Open Source | [Apache-2.0](https://github.com/cloudflare/skills/blob/main/LICENSE) |
| Awesome GitHub Copilot | Scenario / Production-risk | 代码库理解、重构计划、规范提取、Harness Engineering、高风险操作验证 | 明确选择其中一个已检查的开发质量 Skill | [github/awesome-copilot](https://github.com/github/awesome-copilot) | Open Source | [MIT](https://github.com/github/awesome-copilot/blob/main/LICENSE) |
| Agent Skill Eval | Scenario | Skill 安全审计、功能评估、触发测试、版本回归和 Token 成本 | 安装、升级、比较或开发第三方 Skill | [aws-samples/sample-agent-skill-eval](https://github.com/aws-samples/sample-agent-skill-eval) | Open Source | [MIT-0](https://github.com/aws-samples/sample-agent-skill-eval/blob/main/LICENSE) |
| Sentry Agent Skills | Scenario / Production-risk | SDK 接入、Sentry 问题修复、PR 问题处理 | 项目已使用 Sentry | [getsentry/sentry-agent-skills](https://github.com/getsentry/sentry-agent-skills) | Open Source | [Apache-2.0](https://github.com/getsentry/sentry-agent-skills#license) |
| Microsoft Skills | Scenario | Microsoft SDK、Azure、Foundry、MCP Builder | Microsoft 技术栈或 MCP Server 开发 | [microsoft/skills](https://github.com/microsoft/skills) | Open Source | [MIT](https://github.com/microsoft/skills/blob/main/LICENSE) |
| Agent Toolkit for AWS | Scenario | AWS 架构、SDK、IaC、可观测性、安全和 DevSecOps | 项目构建或运行在 AWS | [aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) | Open Source | [Apache-2.0](https://github.com/aws/agent-toolkit-for-aws/blob/main/LICENSE) |

“重点能力”只说明推荐理由，不代表仓库完整内容。大型社区集合必须先选中并检查具体 Skill，不能整仓无条件启用。

## MCP Server

| 项目 | 档位 | 推荐场景 | 仓库 | 许可证类型 | License |
| --- | --- | --- | --- | --- | --- |
| Playwright MCP | Scenario | Web 项目需要真实浏览器操作、截图或端到端验收 | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Open Source | [Apache-2.0](https://github.com/microsoft/playwright-mcp/blob/main/LICENSE) |
| GitHub MCP Server | Scenario | GitHub Issue、PR、Review 或 Actions 协作 | [github/github-mcp-server](https://github.com/github/github-mcp-server) | Open Source | [MIT](https://github.com/github/github-mcp-server/blob/main/LICENSE) |
| CodeGraph | Scenario | 跨文件调用链、影响分析、架构理解或反复检索代码 | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | Open Source | [MIT](https://github.com/colbymchenry/codegraph/blob/main/LICENSE) |
| Semgrep MCP Server | Scenario | 确定性检查代码缺陷、安全问题、敏感信息和项目规则 | [semgrep/semgrep](https://github.com/semgrep/semgrep) | Open Source | [LGPL-2.1](https://github.com/semgrep/semgrep/blob/develop/LICENSE) |
| Context7 | Scenario | 获取当前版本的第三方库文档和代码示例 | [upstash/context7](https://github.com/upstash/context7) | Open Source | [MIT](https://github.com/upstash/context7/blob/master/LICENSE) |
| Grafana MCP | Production-risk | 从指标、日志、Trace、告警和事件中获取线上证据 | [grafana/mcp-grafana](https://github.com/grafana/mcp-grafana) | Open Source | [Apache-2.0](https://github.com/grafana/mcp-grafana/blob/main/LICENSE) |
| SonarQube MCP Server | Scenario | SonarQube 代码质量、安全问题和 Quality Gate | [SonarSource/sonarqube-mcp-server](https://github.com/SonarSource/sonarqube-mcp-server) | Source-Available | [Sonar-Source-Available-1.0](https://github.com/SonarSource/sonarqube-mcp-server/blob/master/LICENSE) |
| Sentry MCP Server | Production-risk | 查询 Sentry Issue、Trace、Release 和项目数据 | [getsentry/sentry-mcp](https://github.com/getsentry/sentry-mcp) | Source-Available | [FSL-1.1-Apache-2.0](https://github.com/getsentry/sentry-mcp/blob/main/LICENSE.md) |
| DBHub | Production-risk | 受控查询 PostgreSQL、MySQL、MariaDB、SQL Server 或 SQLite | [bytebase/dbhub](https://github.com/bytebase/dbhub) | Open Source | [MIT](https://github.com/bytebase/dbhub/blob/main/LICENSE) |

Source-Available 协议说明：

- SonarQube MCP 当前许可非竞争性用途，不是 OSI 开源许可证。
- Sentry MCP 当前版本使用 FSL-1.1，每个版本发布两年后转为 Apache-2.0。

高风险运行要求：

- Grafana、SonarQube 和 Sentry 默认从只读、最小权限凭据开始，需要外部写入时单独确认。
- DBHub 必须使用数据库层只读账号；MCP 自身的 SQL 只读判断不能作为安全边界。配置行数限制和查询超时，并在使用前重新检查其 [SQL Server 只读绕过问题](https://github.com/bytebase/dbhub/issues/349)。
- Context7 会访问托管文档服务，查询中不能携带密钥、专有源码或敏感业务数据。

## 使用规则

1. 先看用户当前目标，再看项目证据；用户明确选择优先。
2. 只推荐并安装能闭合当前场景的最小能力，不因为仓库内容多就全部安装或启用。
3. 安装前重新检查仓库、当前版本许可证、维护状态和具体 Skill/MCP 内容。
4. Source-Available 项目必须确认实际用途符合许可证限制，并在安装时按准确协议名称显式确认。
5. 默认使用项目级安装；全局安装只用于明确需要跨所有项目生效的个人能力。
6. 涉及凭据、外部写入、生产读取或数据库操作时，安装不代表授权执行，执行前仍需明确确认。
