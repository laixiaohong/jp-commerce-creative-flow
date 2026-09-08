# 日本电商创意生产 Flow

将产品证据转成日本电商页面策划、视觉素材与可审核 Demo。基于 [heymio/japan-listing-demo](https://github.com/heymio/japan-listing-demo)，叠加 SwitchBot JP 规则，保留上游升级能力。

## 从这里开始

| 你想做什么 | 去哪里 |
|---|---|
| 开始或继续一个产品页面 | [中文使用指南](../docs/switchbot-jp/QUICKSTART.zh-CN.md) |
| 更新 Flow、同步 Codex、区分两个仓库 | [维护与同步](../docs/switchbot-jp/MAINTENANCE.zh-CN.md) |
| 查看事实、Claim、素材及审批规则 | [SwitchBot JP 规则目录](../overlays/switchbot-jp/manifest.json) |
| 查阅上游完整技术说明 | [上游 README（保留原文）](../README.md) |

### 日常只记一个入口

已安装 Marketing AI Workspace 统一入口时，在 Codex 输入：

```text
$jp-commerce-content-flow
为 XXX 制作 Amazon JP 页面。产品版本：XXX；资料：XXX。
先核对产品事实和缺口，停在人工审核点，暂不生产图片。
```

这个统一入口由 [marketing-ai-workspace](https://github.com/masayukihub/marketing-ai-workspace) 管理，不在本仓库打包范围内。仅独立安装本仓库时，使用 `$jp-commerce-creative-flow`。不用手动调用各个内部 Skill。

## 它负责什么

```text
读取资料 → 整理产品事实 → 应用日本市场规则
→ 页面策划 → 人工审核 → 视觉生产 → 证据与页面验证
```

可以产出页面策略、Gallery / A+ 规划、视觉素材和可审核 HTML Demo；具体产出取决于已批准的范围、证据、素材及运行工具是否齐备。资料缺失或未批准时会停在对应 Gate，不等于可以正式发布。

## 仓库只分三层理解

| 层 | 位置 | 用途 |
|---|---|---|
| 上游生产引擎 | `.agents/skills/` 中的五个上游 Skill | 策划、生产、审核与交付；尽量不改 |
| SwitchBot 定制 | `overlays/switchbot-jp/` 与同名包装入口 | 产品事实、日语市场表达、素材与人工审批规则 |
| 使用与维护 | `docs/switchbot-jp/`、`scripts/`、`.github/workflows/` | 使用说明、打包、测试与上游更新 PR |

不删除内部 Skill 来制造“表面简单”；只让使用者不必理解内部拆分。

## 两条不能省略的边界

- **这是公开仓库。** 不上传真实飞书快照、未发布产品资料、价格、审批记录或产品素材。项目内容放在经过权限确认的私有工作空间。
- **更新不等于批准。** 上游升级经过测试与 PR 人工审核；事实批准、Claim 批准、素材批准、视觉批准和正式发布分别确认。

维护者需要完整操作细节时，再看 [原有操作手册](../docs/switchbot-jp/OPERATIONS.md)。
