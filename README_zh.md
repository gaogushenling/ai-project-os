# AI Project OS

[English](./README.md) | **中文**

一个轻量、可移植的项目级 AI 协作层。项目规则、Skill、MCP 配置和能力版本默认跟随项目，不依赖某台开发机的全局配置。

## 初衷与目标

AI 开发正在从使用单一工具，逐渐变成每个人专属的工作台。不同开发者会选择不同的模型、IDE、Skill、MCP、自动化工具和工作方式；面对的项目、环境和问题也各不相同。个人 AI 开发天然是千人千面的，不应该被强行统一成一套固定流程。

但工具和习惯可以不同，一些基础问题始终存在：AI 如何准确理解当前项目，如何按任务加载必要上下文，如何记住真正有价值的失败与纠偏，如何管理已引入的能力及其风险边界，以及如何用证据确认交付结果。

AI Project OS 的初衷，是为个人 AI 开发工作台提供一个轻量、可移植的项目级底座。这个底座以项目级协作层的形式存在：它把项目事实、上下文路由、有效记忆、能力状态、风险边界和交付验证保存在项目自身，使不同的 AI 工具、IDE 和开发环境都能基于同一份可信信息继续工作。

它不规定唯一的模型、工具链或开发方法，也不试图把所有人的工作台变成同一种形态。它提供的是最小共同基础，让每个人可以在此之上自由组合自己的 AI 开发平台，同时保持项目知识可沉淀、协作过程可延续、能力状态可追踪、交付结果可验证。

它不替代项目文档、开发方法或人的决策，只解决五件事：

- 把项目事实放在项目里，而不是写进全局 skill
- 根据任务按需加载上下文
- 记录真正会影响下一次执行的工具失败和用户纠偏
- 对高风险操作保留明确的确认边界
- 用可执行校验保证协作层没有失效

生成的 `AGENTS.md` 沿用项目级指令文件约定：该约定由 OpenAI Codex 引入（[官方文档](https://developers.openai.com/codex/agents-md)），[GitHub Copilot 也已支持](https://github.blog/changelog/2026-06-23-copilot-coding-agent-now-supports-agents-md-custom-instructions/)——指令文件放在仓库根目录。本协作层在此之上扩展出路由、记忆、能力清单与可执行校验，指令按作用域分层：`AGENTS.md` → `.agents/skills/project-memory` → `docs/ai/`。

## 第一原理

> 让任何 AI 进入一个项目后，都能基于项目自身的真实信息，以最小必要能力，持续交付可使用、可验证、可复现且不越界的结果。

1. **项目是事实载体**：规则、上下文、Skill、MCP 配置和版本跟随项目，不依赖个人全局环境。
2. **目标是产品交付**：衡量标准是用户能否使用、结果能否验收，而不是生成了多少代码。
3. **只引入最小必要能力**：只加载、安装和启用当前项目真正需要的能力。
4. **证据高于声明**：区分代码实现、工程验证、产品验收；没有证据就不提升完成等级。
5. **能力不等于权限**：推荐不等于安装，安装不等于启用，启用不等于允许执行生产操作。
6. **AI 受项目约束**：不擅自扩大范围、修改生产、处理密钥或替用户做高风险决策。

它不应该变成：大而全的 Skill 商店、方法论百科全书、新的重型开发框架、把所有工具全部安装的脚手架，或项目原有文档和工程规范的替代品。

判断是否增加功能只有一个问题：它能否让 AI 更准确地理解项目、更稳定地完成真实任务，或让交付更容易验证？三者都不能，就不加入。

## 产品开发协议

- 从用户真正要获得的结果出发，再决定技术手段。
- 优先交付最小但完整的业务闭环；相关风险按实际影响检查，不机械堆砌设计。
- 关联问题分为当前阻塞、当前必须处理的风险、以后优化，避免任务无限扩大。
- 文档或代码出现冲突时先看时间：用 git 查双方最后改动时间（`git log -1 --format=%cs -- <path>`），新文档通常代表当前生效的方案；旧文档中因方案切换而被遗漏的约束、边界和说明要复核补回，而不是把冲突直接当作矛盾。
- 先讲结论、使用通俗语言，并区分代码实现、工程验证和产品验收。

## 初始化后生成什么

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

只有 8 个核心入口。结构化数据使用标准 JSON，脚本只依赖 Python 标准库；需要 Python 3.11 及以上（CI 在 3.11–3.13 上验证）。

## 可选能力推荐

仓库提供一份小而严的公开源码推荐目录：人类阅读 `references/recommended-integrations.md`，程序读取 `references/recommended-integrations.json`。

- Skill 以源码仓库为推荐单位，MCP Server 作为工具项目单独维护；一个源码仓库只保留一条推荐。
- 收录能核验公开源码、明确许可证和维护方的项目，并区分 Open Source 与 Source-Available。
- Baseline 默认可见，Scenario 按用户意图或项目证据推荐，Production-risk 只在明确的外部服务或生产目标下推荐。
- 推荐项不自动安装、不自动启用；用户明确选择后，默认安装或配置到项目级，并写入项目清单和锁文件。
- 不整仓安装大型 Skill 集合，只复制当前项目选中的子 Skill；全局安装必须由用户明确选择。

查看全部推荐：

```powershell
python scripts/list_recommended_integrations.py
```

按类型、档位或标签筛选：

```powershell
python scripts/list_recommended_integrations.py --type skill-project --tier scenario
python scripts/list_recommended_integrations.py --type mcp-server --tag web --format json
python scripts/list_recommended_integrations.py --license-kind source-available
```

## 项目级安装能力

第三方 Skill 默认安装到项目在 `docs/ai/capabilities.json` 里声明的 `skill_directory`（模板默认 `.agents/skills`）；协作层自带的 project-memory 入口固定在 `.agents/skills/project-memory`，不跟随声明。大型集合必须指定其中一个 Skill：

```powershell
python scripts/install_project_integration.py --target <project-root> --id superpowers --skill systematic-debugging
```

MCP 配置写入项目在 `docs/ai/capabilities.json` 里声明的 `mcp_config` 路径（模板默认 `.codex/config.toml`，使用其他工具时改成该工具的指向即可），安装时默认禁用，只有显式传入 `--enable` 才启用。密钥只写环境变量名称，不写值：

```powershell
python scripts/install_project_integration.py --target <project-root> --id context7 --command npx --arg=-y --arg=@upstash/context7-mcp --env-var CONTEXT7_API_KEY
```

安装结果记录在：

- `docs/ai/capabilities.json`：项目需要什么，以及安装、启用、配置、验证状态。
- `docs/ai/capabilities.lock.json`：具体来源、版本或配置摘要和内容校验值。

“安装完成”不等于“已经验证”。MCP 仍需配置本机环境变量并实际连接；生产读取、外部写入和数据库操作仍需单独授权。

Source-Available 项目还必须使用 `--accept-license <准确协议名称>` 显式确认当前协议；安装器不会把“源码可见”当成无限制开源。

旧版（Codex）项目如果还使用 `.codex/skills/project-memory`，重新运行初始化器会补充新的 `.agents/skills/project-memory`、能力清单和锁文件，不会覆盖已有内容。新路径验证通过后，再自行移除旧副本。

## 使用

### 让 AI 引导接入（推荐）

把本仓库和目标项目一起交给 AI，然后告诉它：

> 请帮我在这个项目中接入 AI Project OS。先只读检查，推荐合适的作用范围，展示预演结果，只在会实质影响结果时让我决策。

仓库根目录的 `AGENTS.md` 会告诉兼容的编程 Agent 如何检查目标项目、选择单仓库或多仓库模式、保留已有规则，并在需要用户做实质决策时停止。完整的人与 AI 使用流程见[入门指南](./docs/getting-started_zh.md)。

### 手动快速接入

写入前先预演：

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

确认后初始化：

```powershell
python scripts/init_project_os.py --target <project-root>
```

在 `docs/ai/project.json` 中补全经过核实的项目事实，检查 `docs/ai/routes.json` 中的任务路由，并且只把会改变未来执行方式的失败或纠偏写入 `docs/ai/memory.json`。

初始化后，在项目中启动 AI 并直接描述任务。兼容的 Agent 会自动应用项目协议；只有工具无法自动加载项目指令时，才需要显式调用 `$ai-project-os` 作为兜底。

校验目标项目：

```powershell
python scripts/validate_project_os.py --target <project-root>
```

严格模式会把未填写的项目占位信息也视为失败：

```powershell
python scripts/validate_project_os.py --target <project-root> --strict
```

校验器还会重算锁文件记录的内容哈希——已安装技能的目录哈希与 MCP 托管配置块哈希，内容漂移直接判失败；锁条目缺少哈希字段则提示警告。

维护本仓库时运行完整自检：

```powershell
python scripts/self_check.py
python -m unittest discover -s tests -v
```

## 设计原则

- `SKILL.md` 只保留跨项目通用协议
- 项目事实、命令和边界归项目所有
- 默认不覆盖已有文件；`--force` 只刷新模板与协议文件，`docs/ai/` 下已填写的状态文件（项目事实、记忆、能力清单与锁文件）永不被初始化器覆盖，需要重置时手动删除对应文件
- 默认安装作用域是项目；全局能力只用于确实跨所有仓库生效的个人偏好
- 不依赖特定操作系统、IDE、模型或私有工具路径；MCP 配置路径与 Skill 目录由项目声明，模板只提供默认值
- 不把密钥、连接串或本机敏感资料写入可提交文件

## 边界与局限

- **协议靠 Agent 自觉执行**：路由匹配、渐进加载和交付门禁由协作工具按指令遵守；校验器只验证数据本身（结构、路径、哈希、密钥），无法验证 Agent 是否真的按协议工作。加任何强制执行手段都会背离最小必要原则，所以这里只做诚实声明。
- **密钥检测是启发式正则**：覆盖协作层自身的已提交文件与日志，可能对形如 `token = ...` 的合法示例误报；它不替代全仓库的专用密钥扫描工具。
- **推荐目录是手工维护的静态数据**：许可证、URL 与状态会随时间过期，因此政策要求安装前重新核对上游（安装器对 Source-Available 强制显式接受协议）。

## 仓库结构

```text
agents/       Codex 展示元数据（可选，仅影响 Codex 展示，其他工具忽略）
assets/       初始化到目标项目的最小模板
scripts/      初始化、校验与自检
tests/        行为测试
```

文档采用双语维护，英文为默认版本；中文译本以 `*_zh.md` 文件随附（`README_zh.md`、`SKILL_zh.md`、`references/recommended-integrations_zh.md`）。

## 社区

本项目在 [LINUX DO](https://linux.do) 社区开源推广。

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
