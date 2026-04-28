# Lipro Docs

仓库文档按读者角色拆分，默认先从根目录 `README.md` / `README_zh.md` 开始。

## 读者入口

| 你要做什么 | 先看这里 | 说明 |
| --- | --- | --- |
| 安装、配置、常见使用 | `README.md` / `README_zh.md` | 面向最终使用者的快速入口 |
| 排障、诊断、反馈问题 | `TROUBLESHOOTING.md` | 用户与贡献者共用的排障说明 |
| 提问、反馈、支持路径 | `../SUPPORT.md` | 支持范围、反馈方式、分流说明 |
| 贡献代码 | `../CONTRIBUTING.md` | 开发环境、校验命令、提交流程 |
| 调整架构边界 | `CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` | 哪些地方能改、改完要验证什么 |
| 了解整体架构 | `NORTH_STAR_TARGET_ARCHITECTURE.md`、`developer_architecture.md` | 一个讲目标，一个讲现状 |
| 安全问题披露 | `../SECURITY.md` | 私密报告路径 |
| 维护者发版 | `MAINTAINER_RELEASE_RUNBOOK.md` | 只面向维护者 |

## 当前文档

- `NORTH_STAR_TARGET_ARCHITECTURE.md`：目标架构与长期约束
- `developer_architecture.md`：当前代码分层与主链说明
- `CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`：贡献者的改动边界地图
- `TROUBLESHOOTING.md`：排障、诊断与问题反馈前检查
- `MAINTAINER_RELEASE_RUNBOOK.md`：发版与维护者操作手册
- `adr/README.md`：长期保留的架构决策记录

## 维护要求

- `README.md` 与 `README_zh.md` 保持信息等价。
- 用户文档优先解释安装、配置、排障，不混入内部治理过程。
- 对外文档链接默认指向仓库中的最新内容，不再固定到旧标签。
