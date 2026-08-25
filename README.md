# AI Project OS

一个轻量、可移植的项目级 AI 协作层。

它不替代项目文档、开发方法或人的决策，只解决五件事：

- 把项目事实放在项目里，而不是写进全局 skill
- 根据任务按需加载上下文
- 记录真正会影响下一次执行的工具失败和用户纠偏
- 对高风险操作保留明确的确认边界
- 用可执行校验保证协作层没有失效

## 产品开发协议

- 从用户真正要获得的结果出发，再决定技术手段。
- 优先交付最小但完整的业务闭环；相关风险按实际影响检查，不机械堆砌设计。
- 关联问题分为当前阻塞、当前必须处理的风险、以后优化，避免任务无限扩大。
- 先讲结论、使用通俗语言，并区分代码实现、工程验证和产品验收。

## 初始化后生成什么

```text
AGENTS.md
.codex/skills/project-memory/SKILL.md
docs/ai/project.json
docs/ai/routes.json
docs/ai/memory.json
docs/ai/logs/YYYY-MM-DD.md
```

只有 6 个核心入口。结构化数据使用标准 JSON，脚本只依赖 Python 标准库。

## 使用

先预演：

```powershell
python scripts/init_project_os.py --target <project-root> --dry-run
```

确认后初始化：

```powershell
python scripts/init_project_os.py --target <project-root>
```

校验目标项目：

```powershell
python scripts/validate_project_os.py --target <project-root>
```

严格模式会把未填写的项目占位信息也视为失败：

```powershell
python scripts/validate_project_os.py --target <project-root> --strict
```

维护本仓库时运行完整自检：

```powershell
python scripts/self_check.py
python -m unittest discover -s tests -v
```

## 设计原则

- `SKILL.md` 只保留跨项目通用协议
- 项目事实、命令和边界归项目所有
- 默认不覆盖已有文件，覆盖必须显式使用 `--force`
- 不依赖特定操作系统、IDE、模型或私有工具路径
- 不把密钥、连接串或本机敏感资料写入可提交文件

## 仓库结构

```text
agents/       Codex 展示元数据
assets/       初始化到目标项目的最小模板
scripts/      初始化、校验与自检
tests/        行为测试
```

## License

Apache-2.0
