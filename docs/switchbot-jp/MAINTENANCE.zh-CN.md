# 维护与同步：只保留两条主线

## 两个仓库各做一件事

| 仓库 | 定位 | 应该修改什么 |
|---|---|---|
| [marketing-ai-workspace](https://github.com/masayukihub/marketing-ai-workspace) | 日常营销入口与共享治理 | 中文入口描述、任务路由、项目契约和共享能力 |
| [jp-commerce-creative-flow](https://github.com/masayukihub/jp-commerce-creative-flow) | 日本电商创意生产引擎与 SwitchBot Overlay | 定制规则、生产引擎兼容性和上游升级 |

不要把两个仓库的 Skill 全部复制到一起，也不要把“入口合并”理解为删除策划、生产、审核模块。模板和执行代码由原有模块继续负责。

## 主线一：上游升级

```text
heymio/japan-listing-demo
→ 拉取与比较 → 兼容性分析 → 回归测试
→ Draft PR → 人工审核 → 合并本仓库 main
```

现有 [upstream-sync.yml](../../.github/workflows/upstream-sync.yml) 配置了每周检查及手动触发。是否实际运行成功，要查看 Actions 日志与权限；配置存在不代表同步成功。冲突时停止，不自动合并到 main。

可直接对 Codex 说：

```text
检查 jp-commerce-creative-flow 的 upstream 更新。
保留 SwitchBot Overlay，在独立分支做兼容性分析和回归测试，创建 Draft PR，不合并。
```

## 主线二：已审核版本同步到 Codex

```text
仓库独立分支修改 → 测试 → PR 审核 → main
→ 检查本机差异 → 同步对应运行目录 → 验证入口与依赖
```

- Marketing AI Workspace 的统一入口使用该仓库已有的受控镜像同步工具。
- 本仓库的内部引擎可能通过链接或安装包被调用；先检查实际来源再更新，不能假定“合并 GitHub”就自动更新本机。
- 若使用链接，确认链接指向经过审核的 checkout，而不是实验分支；若使用安装包，需重新构建并更新安装。
- 更新前保留可回退版本，发现本机独有改动先比较，不盲目覆盖。

可直接说：

```text
检查 GitHub main 与我的 Codex 电商内容入口、内部生产引擎是否一致。
只同步已审核 main；保留本机独有改动，报告版本、差异和验证结果。
```

## 项目内容不是 Skill 更新

本仓库为公开仓库，只放可公开规则、Schema、脚本、合成测试与空模板。

产品事实、真实飞书快照、未批准 Claim、审批记录、项目图片及商业价格应保存在权限明确的私有项目位置。要同步 GitHub，先确认目标私有仓库与数据范围，再通过独立 PR 审核；不自动上传整个 Codex 聊天或产品目录。

## 本次简化范围

新增 `.github/README.md` 作为 GitHub 优先展示的中文首页，保留根目录上游 README 原文，减少未来同步冲突。另新增本说明和中文使用指南。

不改 Skill 名称、路由、Gate 顺序、生产代码、审批状态或上游链接；不删除历史文档、不新增平台或自动发布功能。

[返回中文首页](../../.github/README.md) · [原有维护细节](OPERATIONS.md)
