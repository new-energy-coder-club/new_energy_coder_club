# 治理与决策（Governance）
- 角色：Maintainers / Contributors / Members
- 决策：重要事项经维护者评审与共识
- 流程：Issue提议 → 讨论 → 决议 → 执行 → 复盘
- 节奏：周会/例会记录与公开

## 分支模型（Branch Model）

> 主仓：Gitee `origin/master`；GitHub `github/master` 为镜像（CI 在 GitHub Actions 运行）。

| 分支 | 用途 | 规则 |
|---|---|---|
| `master` | 主干：文档、社区资产、稳定项目代码 | 一切 PR 的默认目标；保持随时可发布 |
| `feat/*` | 短期功能/专题分支（如 `feat/curc2027-onboarding`） | 完成后合回 master 并删除；生命周期 ≤1 个赛季 |
| `2026RC-CODE` 等赛季分支 | 竞赛代码赛季隔离 | 赛季结束后归档，不再合回 |
| `main`、`feat/ssg-*` | **独立历史线：NEC 官网（Vite SSG）** | 与 master 不互通；官网相关 PR 才使用 |
| `SKill` | AI Agent Skills 开发支线（worktree 开发） | 独立于主干节奏 |

**给新人的判断口诀**：改文档/项目代码 → 基于 `master`；改官网 → 基于 `main`；竞赛赛季代码 → 问对应 SIG 负责人确认赛季分支。

## OSPP 参与

开源之夏相关治理（课题申报、导师职责、学生评审）见 [docs/ospp/](./ospp/)。
