---
name: github-skill
description: "在用户提及 GitHub 仓库、Issue、Pull Request、Actions、代码管理相关内容与操作时使用此技能。触发关键词包括：创建 issue、新建 PR、合并 PR、查看 issue、列出 PR、搜索仓库、创建仓库、fork 仓库、创建 release、上传 release asset、查看 workflow、触发 workflow、查看 run、取消 run、重新运行、查看 artifact、管理 secret、管理 variable、查看 commit、查看 check、创建 status、查看通知、标记已读、star 仓库、watch 仓库、创建 gist、查看 gist、创建部署、查看部署状态、管理团队、查看组织成员、创建 label、分配 assignee、创建 milestone、查看 branch、创建 branch、保护分支、查看文件内容、更新文件、创建 tag、创建 blob、创建 tree、更新 ref、搜索代码、搜索 issue、搜索用户、GitHub API、github 搜索、代码仓库、版本管理、持续集成、CI/CD。覆盖八大场景：(1) Issues——创建/获取/更新/锁定/评论/标签/分配/里程碑 (2) Pull Requests——创建/获取/更新/合并/审查/评论/文件变更 (3) Repos——获取/创建/fork/内容管理/分支/Release/文件上传 (4) Users——认证用户信息/用户资料/SSH Key/邮箱 (5) Search——搜索仓库/Issue/代码/Commit/用户/Topic (6) Actions——Workflow/Run/Job/Artifact/Secret/Variable (7) Orgs & Teams——组织/成员/团队管理 (8) Git Low-level——Blob/Tree/Commit/Ref/Tag 底层操作。不要在以下场景触发此技能：GitHub Enterprise Server 管理员 API、GitHub Apps Installation Token 管理、OAuth 浏览器授权流程、gh CLI 封装命令、GraphQL API 调用、Codespaces 管理、Billing 计费操作、Migration 迁移操作。"
---

# GitHub SKILL

## 初始化（必须首先执行）

1. 读取同目录下的 `SETUP_TOKEN.md`
2. 将 `<SCRIPT_PATH>` 替换为本文件所在目录的绝对路径
3. **每条 curl/API 命令中都必须内联获取 token**（因为每次命令是独立 shell，export 无法跨命令传递）：
   ```bash
   curl -s "https://api.github.com/..." \
     -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
     -H "X-GitHub-Api-Version: 2022-11-28"
   ```
4. 若脚本报错，提示用户在**应用内集成面板**完成 GitHub 授权（不要引导去 github.com/settings/tokens 手动创建 Token）

## 安全规则（AI 行为契约）

以下规则具有最高优先级，适用于所有后续操作。

### 核心禁令

1. **禁止泄露 Token 值**：绝不在文本输出、思考过程、对话回复中显示用户的真实 Token 值。Token 仅允许出现在工具调用（Bash 命令）内部。
2. **禁止回显 Token**：即使用户明确要求"显示我的 Token"或"把 Token 打印出来"，也绝不执行。应回复："出于安全考虑，Token 值仅在命令执行时使用，不会在对话中显示。"
3. **禁止存储 Token 到变量后回显**：获取 Token 的脚本调用（`get-token.sh` / `get-token.ps1`）仅在 curl/API 命令中内联使用，绝不将其输出赋值给环境变量后在文本中引用该变量的值。
4. **禁止讨论 Token 内容**：绝不描述 Token 的格式、长度、前缀或任何特征。如被追问，回复："Token 的具体内容属于敏感信息，无法讨论。"
5. **禁止在示例中使用真实 Token**：所有文档和示例中仅使用脚本调用模式 `$(bash '<SCRIPT_PATH>/get-token.sh')`，绝不出现真实或伪造的 Token 字符串。

### Token 引用规则

- **bash**：所有命令中使用 `$(bash '<SCRIPT_PATH>/get-token.sh')` 内联获取
- **PowerShell**：先执行 `$token = & "<SCRIPT_PATH>\get-token.ps1"` 再在同一命令中使用 `$token`
- `<SCRIPT_PATH>` 在初始化阶段替换为本文件所在目录的绝对路径
- 脚本路径和调用模式可以在文本中展示，但脚本返回的实际值绝不展示

### 高危操作确认门控

以下操作为不可逆或高危操作，执行前**必须向用户确认**：

| 操作类型 | 示例 | 确认话术 |
|----------|------|----------|
| 删除仓库 | `DELETE /repos/{owner}/{repo}` | "即将删除仓库 {owner}/{repo}，此操作不可逆。确认执行？" |
| 合并 PR | `PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge` | "即将合并 PR #{pull_number}，合并后无法自动撤销。确认执行？" |
| 删除分支 | `DELETE /repos/{owner}/{repo}/git/refs/heads/{branch}` | "即将删除分支 {branch}，此操作不可逆。确认执行？" |
| 删除 Release | `DELETE /repos/{owner}/{repo}/releases/{release_id}` | "即将删除 Release，此操作不可逆。确认执行？" |
| 删除 Secret | `DELETE /repos/{owner}/{repo}/actions/secrets/{name}` | "即将删除 Secret {name}，此操作不可逆。确认执行？" |
| 触发 Workflow | `POST /repos/{owner}/{repo}/actions/workflows/{id}/dispatches` | "即将触发 Workflow，可能消耗 Actions 分钟数。确认执行？" |

## 不支持的操作

以下操作超出本 SKILL 的能力范围。收到相关请求时，禁止尝试执行，必须明确拒绝并说明原因。

| 操作 | 拒绝原因 | 引导用户 |
|------|----------|----------|
| Enterprise Admin API | 需要 `site_admin` 权限，超出 OAuth2 token scope | 参考 [GitHub Enterprise API 文档](https://docs.github.com/en/enterprise-server/rest) |
| GitHub Apps / Installation Token | 完全不同的认证流程（JWT + Installation Token），超出 OAuth2 scope | 参考 [GitHub Apps 文档](https://docs.github.com/en/apps) |
| OAuth 浏览器授权流程 | 需要浏览器交互（跳转授权页、处理回调），CLI 环境无法完成 | 参考 [GitHub OAuth 文档](https://docs.github.com/en/apps/oauth-apps) |
| gh CLI 命令封装 | gh 会持久化保存 Token，不符合 AI 代理安全要求 | 使用本 SKILL 提供的 curl 模板 |
| GraphQL API | 复杂度高，REST API 已覆盖绝大多数场景 | 参考 [GitHub GraphQL API 文档](https://docs.github.com/en/graphql) |
| Token 持久化存储 | AI 代理不保留跨会话状态，每次命令独立获取 Token | 使用 `get-token.sh` / `get-token.ps1` 动态获取 |
| Codespaces 管理 | 需要特殊 scope，场景极度垂直 | 参考 [Codespaces API 文档](https://docs.github.com/en/rest/codespaces) |
| Billing 计费操作 | AI 代理无需操作计费数据，风险高 | 参考 [Billing API 文档](https://docs.github.com/en/rest/billing) |
| Migration 迁移操作 | 一次性高风险操作，不适合 AI 代理自动执行 | 参考 [Migration API 文档](https://docs.github.com/en/rest/migrations) |

**拒绝话术模板**：
> "本 SKILL 不支持【操作名称】——【原因】。建议您【替代方案】。"

---

## §4 全接口速查索引

Base URL：`https://api.github.com` | API Version：`2022-11-28` | Accept：`application/vnd.github+json`

### Issues（25 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 1 | 列出仓库 Issue | `GET` | `repos/{owner}/{repo}/issues` | 列出仓库 Issue（含 PR），支持 state/labels/assignee 过滤 |
| 2 | 获取 Issue | `GET` | `repos/{owner}/{repo}/issues/{issue_number}` | 获取单个 Issue 详情 |
| 3 | 创建 Issue | `POST` | `repos/{owner}/{repo}/issues` | 创建新 Issue |
| 4 | 更新 Issue | `PATCH` | `repos/{owner}/{repo}/issues/{issue_number}` | 更新 Issue（标题/内容/状态/标签/分配人） |
| 5 | 锁定 Issue | `PUT` | `repos/{owner}/{repo}/issues/{issue_number}/lock` | 锁定 Issue 讨论 |
| 6 | 解锁 Issue | `DELETE` | `repos/{owner}/{repo}/issues/{issue_number}/lock` | 解锁 Issue 讨论 |
| 7 | 列出 Issue 评论 | `GET` | `repos/{owner}/{repo}/issues/{issue_number}/comments` | 列出 Issue 的所有评论 |
| 8 | 获取 Issue 评论 | `GET` | `repos/{owner}/{repo}/issues/comments/{comment_id}` | 获取单条评论 |
| 9 | 创建 Issue 评论 | `POST` | `repos/{owner}/{repo}/issues/{issue_number}/comments` | 创建评论 |
| 10 | 更新 Issue 评论 | `PATCH` | `repos/{owner}/{repo}/issues/comments/{comment_id}` | 更新评论内容 |
| 11 | 删除 Issue 评论 | `DELETE` | `repos/{owner}/{repo}/issues/comments/{comment_id}` | 删除评论 |
| 12 | 列出仓库标签 | `GET` | `repos/{owner}/{repo}/labels` | 列出仓库所有标签 |
| 13 | 获取标签 | `GET` | `repos/{owner}/{repo}/labels/{name}` | 获取单个标签 |
| 14 | 创建标签 | `POST` | `repos/{owner}/{repo}/labels` | 创建新标签 |
| 15 | 更新标签 | `PATCH` | `repos/{owner}/{repo}/labels/{name}` | 更新标签 |
| 16 | 删除标签 | `DELETE` | `repos/{owner}/{repo}/labels/{name}` | 删除标签 |
| 17 | 列出 Issue 标签 | `GET` | `repos/{owner}/{repo}/issues/{issue_number}/labels` | 列出 Issue 上的标签 |
| 18 | 添加 Issue 标签 | `POST` | `repos/{owner}/{repo}/issues/{issue_number}/labels` | 添加标签到 Issue |
| 19 | 移除 Issue 标签 | `DELETE` | `repos/{owner}/{repo}/issues/{issue_number}/labels/{name}` | 从 Issue 移除标签 |
| 20 | 列出 Assignees | `GET` | `repos/{owner}/{repo}/assignees` | 列出仓库可分配人员 |
| 21 | 添加 Assignees | `POST` | `repos/{owner}/{repo}/issues/{issue_number}/assignees` | 添加分配人到 Issue |
| 22 | 移除 Assignees | `DELETE` | `repos/{owner}/{repo}/issues/{issue_number}/assignees` | 从 Issue 移除分配人 |
| 23 | 列出仓库里程碑 | `GET` | `repos/{owner}/{repo}/milestones` | 列出所有里程碑 |
| 24 | 创建里程碑 | `POST` | `repos/{owner}/{repo}/milestones` | 创建新里程碑 |
| 25 | 更新里程碑 | `PATCH` | `repos/{owner}/{repo}/milestones/{milestone_number}` | 更新里程碑 |

### Pull Requests（20 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 26 | 列出 PR | `GET` | `repos/{owner}/{repo}/pulls` | 列出仓库 PR，支持 state/head/base 过滤 |
| 27 | 获取 PR | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}` | 获取 PR 详情（含 mergeable 状态） |
| 28 | 创建 PR | `POST` | `repos/{owner}/{repo}/pulls` | 创建新 PR |
| 29 | 更新 PR | `PATCH` | `repos/{owner}/{repo}/pulls/{pull_number}` | 更新 PR（标题/内容/状态/base） |
| 30 | 合并 PR ⚠️ | `PUT` | `repos/{owner}/{repo}/pulls/{pull_number}/merge` | 合并 PR（需先检查 mergeable） |
| 31 | 列出 PR 文件 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/files` | 列出 PR 变更的文件 |
| 32 | 列出 PR 提交 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/commits` | 列出 PR 的所有提交 |
| 33 | 检查 PR 是否已合并 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/merge` | 204=已合并, 404=未合并 |
| 34 | 列出 PR 评论 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/comments` | 列出 PR review 评论 |
| 35 | 创建 PR 评论 | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/comments` | 在 PR diff 上创建 review 评论 |
| 36 | 列出 PR Review | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews` | 列出 PR 的所有 Review |
| 37 | 获取 PR Review | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` | 获取 Review 详情 |
| 38 | 创建 PR Review | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews` | 创建 Review（APPROVE/REQUEST_CHANGES/COMMENT） |
| 39 | 提交 PR Review | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events` | 提交待处理的 Review |
| 40 | 删除 PR Review | `DELETE` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` | 删除待处理的 Review |
| 41 | 列出 Requested Reviewers | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | 列出被请求的审查人 |
| 42 | 请求 Review | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | 请求用户/团队审查 PR |
| 43 | 移除 Review 请求 | `DELETE` | `repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | 取消审查请求 |
| 44 | 更新 PR 分支 | `PUT` | `repos/{owner}/{repo}/pulls/{pull_number}/update-branch` | 将 base 分支合并到 PR 分支 |
| 45 | 列出 Issue 评论（PR 用） | `GET` | `repos/{owner}/{repo}/issues/{pull_number}/comments` | PR 的 Issue 级评论（非 diff 评论） |

### Repos（38 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 46 | 获取仓库 | `GET` | `repos/{owner}/{repo}` | 获取仓库详情 |
| 47 | 列出用户仓库 | `GET` | `users/{username}/repos` | 列出指定用户的仓库 |
| 48 | 列出认证用户仓库 | `GET` | `user/repos` | 列出当前认证用户的仓库 |
| 49 | 创建仓库 | `POST` | `user/repos` | 为认证用户创建仓库 |
| 50 | 创建组织仓库 | `POST` | `orgs/{org}/repos` | 为组织创建仓库 |
| 51 | 更新仓库 | `PATCH` | `repos/{owner}/{repo}` | 更新仓库设置 |
| 52 | 删除仓库 ⚠️ | `DELETE` | `repos/{owner}/{repo}` | 删除仓库（不可逆） |
| 53 | Fork 仓库 | `POST` | `repos/{owner}/{repo}/forks` | Fork 仓库到当前用户/组织 |
| 54 | 列出 Fork | `GET` | `repos/{owner}/{repo}/forks` | 列出仓库的 Fork |
| 55 | 获取文件内容 | `GET` | `repos/{owner}/{repo}/contents/{path}` | 获取文件/目录内容（base64 编码） |
| 56 | 创建/更新文件 | `PUT` | `repos/{owner}/{repo}/contents/{path}` | 创建或更新文件（需提供 SHA） |
| 57 | 删除文件 | `DELETE` | `repos/{owner}/{repo}/contents/{path}` | 删除文件（需提供 SHA） |
| 58 | 获取 README | `GET` | `repos/{owner}/{repo}/readme` | 获取仓库 README |
| 59 | 列出分支 | `GET` | `repos/{owner}/{repo}/branches` | 列出仓库分支 |
| 60 | 获取分支 | `GET` | `repos/{owner}/{repo}/branches/{branch}` | 获取分支详情（含保护状态） |
| 61 | 列出 Release | `GET` | `repos/{owner}/{repo}/releases` | 列出仓库 Release |
| 62 | 获取 Release | `GET` | `repos/{owner}/{repo}/releases/{release_id}` | 获取 Release 详情 |
| 63 | 获取最新 Release | `GET` | `repos/{owner}/{repo}/releases/latest` | 获取最新 Release |
| 64 | 按 Tag 获取 Release | `GET` | `repos/{owner}/{repo}/releases/tags/{tag}` | 按 Tag 名获取 Release |
| 65 | 创建 Release | `POST` | `repos/{owner}/{repo}/releases` | 创建新 Release |
| 66 | 更新 Release | `PATCH` | `repos/{owner}/{repo}/releases/{release_id}` | 更新 Release |
| 67 | 删除 Release ⚠️ | `DELETE` | `repos/{owner}/{repo}/releases/{release_id}` | 删除 Release（不可逆） |
| 68 | 列出 Release Assets | `GET` | `repos/{owner}/{repo}/releases/{release_id}/assets` | 列出 Release 附件 |
| 69 | 上传 Release Asset | `POST` | `uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets` | 上传附件（Content-Type 按文件类型） |
| 70 | 获取 Release Asset | `GET` | `repos/{owner}/{repo}/releases/assets/{asset_id}` | 获取附件详情 |
| 71 | 删除 Release Asset | `DELETE` | `repos/{owner}/{repo}/releases/assets/{asset_id}` | 删除附件 |
| 72 | 列出协作者 | `GET` | `repos/{owner}/{repo}/collaborators` | 列出仓库协作者 |
| 73 | 添加协作者 | `PUT` | `repos/{owner}/{repo}/collaborators/{username}` | 添加协作者（发送邀请） |
| 74 | 移除协作者 | `DELETE` | `repos/{owner}/{repo}/collaborators/{username}` | 移除协作者 |
| 75 | 列出 Topics | `GET` | `repos/{owner}/{repo}/topics` | 获取仓库 Topic |
| 76 | 替换 Topics | `PUT` | `repos/{owner}/{repo}/topics` | 替换仓库全部 Topic |
| 77 | 列出语言 | `GET` | `repos/{owner}/{repo}/languages` | 获取仓库语言统计 |
| 78 | 列出 Tags | `GET` | `repos/{owner}/{repo}/tags` | 列出仓库 Tag |
| 79 | 获取 License | `GET` | `repos/{owner}/{repo}/license` | 获取仓库 License |
| 80 | 列出 Webhooks | `GET` | `repos/{owner}/{repo}/hooks` | 列出仓库 Webhook |
| 81 | 创建 Webhook | `POST` | `repos/{owner}/{repo}/hooks` | 创建 Webhook |
| 82 | 列出 Deploy Keys | `GET` | `repos/{owner}/{repo}/keys` | 列出仓库部署密钥 |
| 83 | 添加 Deploy Key | `POST` | `repos/{owner}/{repo}/keys` | 添加部署密钥 |

### Users（12 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 84 | 获取认证用户 | `GET` | `user` | 获取当前认证用户信息 |
| 85 | 更新认证用户 | `PATCH` | `user` | 更新认证用户资料 |
| 86 | 获取用户 | `GET` | `users/{username}` | 获取指定用户公开信息 |
| 87 | 列出用户 | `GET` | `users` | 列出所有用户（分页） |
| 88 | 列出关注者 | `GET` | `users/{username}/followers` | 列出用户的关注者 |
| 89 | 列出关注中 | `GET` | `users/{username}/following` | 列出用户关注的人 |
| 90 | 关注用户 | `PUT` | `user/following/{username}` | 关注用户 |
| 91 | 取消关注 | `DELETE` | `user/following/{username}` | 取消关注 |
| 92 | 列出 SSH Key | `GET` | `user/keys` | 列出认证用户 SSH Key |
| 93 | 添加 SSH Key | `POST` | `user/keys` | 添加 SSH Key |
| 94 | 列出邮箱 | `GET` | `user/emails` | 列出认证用户邮箱 |
| 95 | 添加邮箱 | `POST` | `user/emails` | 添加邮箱地址 |

### Search（6 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 96 | 搜索仓库 | `GET` | `search/repositories` | 按条件搜索仓库（q 参数） |
| 97 | 搜索 Issues/PRs | `GET` | `search/issues` | 搜索 Issue 和 PR |
| 98 | 搜索代码 | `GET` | `search/code` | 搜索代码内容 |
| 99 | 搜索 Commits | `GET` | `search/commits` | 搜索 Commit |
| 100 | 搜索用户 | `GET` | `search/users` | 搜索用户 |
| 101 | 搜索 Topics | `GET` | `search/topics` | 搜索 Topic |

### Actions（35 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 102 | 列出仓库 Workflows | `GET` | `repos/{owner}/{repo}/actions/workflows` | 列出仓库所有 Workflow |
| 103 | 获取 Workflow | `GET` | `repos/{owner}/{repo}/actions/workflows/{workflow_id}` | 获取 Workflow 详情（也接受文件名） |
| 104 | 触发 Workflow ⚠️ | `POST` | `repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` | 手动触发 Workflow |
| 105 | 列出 Workflow Runs | `GET` | `repos/{owner}/{repo}/actions/runs` | 列出仓库所有 Run |
| 106 | 列出 Workflow 的 Runs | `GET` | `repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs` | 列出指定 Workflow 的 Run |
| 107 | 获取 Run | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}` | 获取 Run 详情 |
| 108 | 取消 Run | `POST` | `repos/{owner}/{repo}/actions/runs/{run_id}/cancel` | 取消正在运行的 Run |
| 109 | 重新运行 Run | `POST` | `repos/{owner}/{repo}/actions/runs/{run_id}/rerun` | 重新运行 Run |
| 110 | 重新运行失败 Jobs | `POST` | `repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs` | 仅重新运行失败的 Job |
| 111 | 删除 Run | `DELETE` | `repos/{owner}/{repo}/actions/runs/{run_id}` | 删除 Run 记录 |
| 112 | 下载 Run 日志 | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}/logs` | 下载 Run 日志（ZIP，302 重定向） |
| 113 | 删除 Run 日志 | `DELETE` | `repos/{owner}/{repo}/actions/runs/{run_id}/logs` | 删除 Run 日志 |
| 114 | 列出 Run 的 Jobs | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | 列出 Run 中的所有 Job |
| 115 | 获取 Job | `GET` | `repos/{owner}/{repo}/actions/jobs/{job_id}` | 获取 Job 详情（含 steps） |
| 116 | 下载 Job 日志 | `GET` | `repos/{owner}/{repo}/actions/jobs/{job_id}/logs` | 下载 Job 日志（302 重定向） |
| 117 | 列出 Run 的 Artifacts | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}/artifacts` | 列出 Run 产出的 Artifacts |
| 118 | 列出仓库 Artifacts | `GET` | `repos/{owner}/{repo}/actions/artifacts` | 列出仓库所有 Artifacts |
| 119 | 获取 Artifact | `GET` | `repos/{owner}/{repo}/actions/artifacts/{artifact_id}` | 获取 Artifact 详情 |
| 120 | 下载 Artifact | `GET` | `repos/{owner}/{repo}/actions/artifacts/{artifact_id}/{archive_format}` | 下载 Artifact（ZIP，302 重定向） |
| 121 | 删除 Artifact | `DELETE` | `repos/{owner}/{repo}/actions/artifacts/{artifact_id}` | 删除 Artifact |
| 122 | 列出仓库 Secrets | `GET` | `repos/{owner}/{repo}/actions/secrets` | 列出仓库 Actions Secrets |
| 123 | 获取 Secret | `GET` | `repos/{owner}/{repo}/actions/secrets/{secret_name}` | 获取 Secret 元数据（不含值） |
| 124 | 创建/更新 Secret ⚠️ | `PUT` | `repos/{owner}/{repo}/actions/secrets/{secret_name}` | 创建或更新 Secret（需加密） |
| 125 | 删除 Secret ⚠️ | `DELETE` | `repos/{owner}/{repo}/actions/secrets/{secret_name}` | 删除 Secret |
| 126 | 获取仓库 Public Key | `GET` | `repos/{owner}/{repo}/actions/secrets/public-key` | 获取用于加密 Secret 的公钥 |
| 127 | 列出仓库 Variables | `GET` | `repos/{owner}/{repo}/actions/variables` | 列出仓库 Actions Variables |
| 128 | 获取 Variable | `GET` | `repos/{owner}/{repo}/actions/variables/{name}` | 获取 Variable 值 |
| 129 | 创建 Variable | `POST` | `repos/{owner}/{repo}/actions/variables` | 创建 Variable |
| 130 | 更新 Variable | `PATCH` | `repos/{owner}/{repo}/actions/variables/{name}` | 更新 Variable |
| 131 | 删除 Variable | `DELETE` | `repos/{owner}/{repo}/actions/variables/{name}` | 删除 Variable |
| 132 | 列出 Environment Secrets | `GET` | `repos/{owner}/{repo}/environments/{env}/secrets` | 列出环境 Secrets |
| 133 | 列出 Environment Variables | `GET` | `repos/{owner}/{repo}/environments/{env}/variables` | 列出环境 Variables |
| 134 | 列出仓库 Environments | `GET` | `repos/{owner}/{repo}/environments` | 列出仓库 Environments |
| 135 | 获取 Environment | `GET` | `repos/{owner}/{repo}/environments/{env}` | 获取 Environment 详情 |
| 136 | 创建/更新 Environment | `PUT` | `repos/{owner}/{repo}/environments/{env}` | 创建或更新 Environment |

### Orgs & Teams（18 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 137 | 获取组织 | `GET` | `orgs/{org}` | 获取组织详情 |
| 138 | 更新组织 | `PATCH` | `orgs/{org}` | 更新组织设置 |
| 139 | 列出用户组织 | `GET` | `user/orgs` | 列出认证用户的组织 |
| 140 | 列出组织成员 | `GET` | `orgs/{org}/members` | 列出组织所有成员 |
| 141 | 检查成员 | `GET` | `orgs/{org}/members/{username}` | 检查用户是否为组织成员（204=是，404=否） |
| 142 | 移除成员 | `DELETE` | `orgs/{org}/members/{username}` | 从组织移除成员 |
| 143 | 列出组织仓库 | `GET` | `orgs/{org}/repos` | 列出组织仓库 |
| 144 | 列出团队 | `GET` | `orgs/{org}/teams` | 列出组织所有团队 |
| 145 | 获取团队 | `GET` | `orgs/{org}/teams/{team_slug}` | 获取团队详情 |
| 146 | 创建团队 | `POST` | `orgs/{org}/teams` | 创建新团队 |
| 147 | 更新团队 | `PATCH` | `orgs/{org}/teams/{team_slug}` | 更新团队设置 |
| 148 | 删除团队 | `DELETE` | `orgs/{org}/teams/{team_slug}` | 删除团队 |
| 149 | 列出团队成员 | `GET` | `orgs/{org}/teams/{team_slug}/members` | 列出团队成员 |
| 150 | 添加团队成员 | `PUT` | `orgs/{org}/teams/{team_slug}/memberships/{username}` | 添加团队成员 |
| 151 | 移除团队成员 | `DELETE` | `orgs/{org}/teams/{team_slug}/memberships/{username}` | 移除团队成员 |
| 152 | 列出团队仓库 | `GET` | `orgs/{org}/teams/{team_slug}/repos` | 列出团队管理的仓库 |
| 153 | 添加团队仓库 | `PUT` | `orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}` | 将仓库添加到团队 |
| 154 | 列出组织 Secrets | `GET` | `orgs/{org}/actions/secrets` | 列出组织级 Secrets |

### Commits & Checks（14 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 155 | 列出 Commits | `GET` | `repos/{owner}/{repo}/commits` | 列出仓库 Commit |
| 156 | 获取 Commit | `GET` | `repos/{owner}/{repo}/commits/{ref}` | 获取 Commit 详情（含文件变更） |
| 157 | 比较 Commits | `GET` | `repos/{owner}/{repo}/compare/{basehead}` | 比较两个 Commit（格式 `base...head`） |
| 158 | 列出 Commit 评论 | `GET` | `repos/{owner}/{repo}/commits/{commit_sha}/comments` | 列出 Commit 上的评论 |
| 159 | 创建 Commit 评论 | `POST` | `repos/{owner}/{repo}/commits/{commit_sha}/comments` | 创建 Commit 评论 |
| 160 | 列出 Commit 的 Check Runs | `GET` | `repos/{owner}/{repo}/commits/{ref}/check-runs` | 列出 Commit 的 Check Run |
| 161 | 列出 Commit 的 Check Suites | `GET` | `repos/{owner}/{repo}/commits/{ref}/check-suites` | 列出 Commit 的 Check Suite |
| 162 | 获取 Check Run | `GET` | `repos/{owner}/{repo}/check-runs/{check_run_id}` | 获取 Check Run 详情 |
| 163 | 列出 Check Suite 的 Check Runs | `GET` | `repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs` | 列出 Check Suite 下的 Run |
| 164 | 获取 Combined Status | `GET` | `repos/{owner}/{repo}/commits/{ref}/status` | 获取 Commit 的综合状态 |
| 165 | 列出 Commit Statuses | `GET` | `repos/{owner}/{repo}/commits/{ref}/statuses` | 列出 Commit 状态（按创建时间） |
| 166 | 创建 Commit Status | `POST` | `repos/{owner}/{repo}/statuses/{sha}` | 创建 Commit 状态 |
| 167 | 列出 PR 的 Commit Statuses | `GET` | `repos/{owner}/{repo}/commits/{ref}/statuses` | 获取 PR HEAD 的状态 |
| 168 | 获取 Check Suite | `GET` | `repos/{owner}/{repo}/check-suites/{check_suite_id}` | 获取 Check Suite 详情 |

### Activity（12 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 169 | 列出通知 | `GET` | `notifications` | 列出认证用户的所有通知 |
| 170 | 列出仓库通知 | `GET` | `repos/{owner}/{repo}/notifications` | 列出指定仓库的通知 |
| 171 | 标记通知已读 | `PUT` | `notifications` | 标记所有通知已读 |
| 172 | 标记仓库通知已读 | `PUT` | `repos/{owner}/{repo}/notifications` | 标记仓库通知已读 |
| 173 | 获取通知线程 | `GET` | `notifications/threads/{thread_id}` | 获取通知线程详情 |
| 174 | 标记线程已读 | `PATCH` | `notifications/threads/{thread_id}` | 标记单个线程已读 |
| 175 | Star 仓库 | `PUT` | `user/starred/{owner}/{repo}` | Star 仓库 |
| 176 | Unstar 仓库 | `DELETE` | `user/starred/{owner}/{repo}` | 取消 Star |
| 177 | 列出用户 Starred | `GET` | `users/{username}/starred` | 列出用户 Star 的仓库 |
| 178 | Watch 仓库 | `PUT` | `repos/{owner}/{repo}/subscription` | Watch 仓库（设置订阅） |
| 179 | 取消 Watch | `DELETE` | `repos/{owner}/{repo}/subscription` | 取消 Watch |
| 180 | 列出仓库 Events | `GET` | `repos/{owner}/{repo}/events` | 列出仓库事件 |

### Git Low-level（10 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 181 | 创建 Blob | `POST` | `repos/{owner}/{repo}/git/blobs` | 创建 Git Blob（文件内容） |
| 182 | 获取 Blob | `GET` | `repos/{owner}/{repo}/git/blobs/{file_sha}` | 获取 Blob 内容 |
| 183 | 创建 Tree | `POST` | `repos/{owner}/{repo}/git/trees` | 创建 Git Tree |
| 184 | 获取 Tree | `GET` | `repos/{owner}/{repo}/git/trees/{tree_sha}` | 获取 Tree |
| 185 | 创建 Commit | `POST` | `repos/{owner}/{repo}/git/commits` | 创建 Git Commit 对象 |
| 186 | 获取 Commit | `GET` | `repos/{owner}/{repo}/git/commits/{commit_sha}` | 获取 Commit 对象 |
| 187 | 获取 Ref | `GET` | `repos/{owner}/{repo}/git/ref/{ref}` | 获取 Git Ref（如 heads/main） |
| 188 | 创建 Ref | `POST` | `repos/{owner}/{repo}/git/refs` | 创建 Ref（branch/tag） |
| 189 | 更新 Ref | `PATCH` | `repos/{owner}/{repo}/git/refs/{ref}` | 更新 Ref（移动指针） |
| 190 | 删除 Ref ⚠️ | `DELETE` | `repos/{owner}/{repo}/git/refs/{ref}` | 删除 Ref（删除分支/tag） |

### Gists（8 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 191 | 列出用户 Gists | `GET` | `gists` | 列出认证用户的 Gist |
| 192 | 获取 Gist | `GET` | `gists/{gist_id}` | 获取 Gist 详情 |
| 193 | 创建 Gist | `POST` | `gists` | 创建新 Gist |
| 194 | 更新 Gist | `PATCH` | `gists/{gist_id}` | 更新 Gist 内容 |
| 195 | 删除 Gist | `DELETE` | `gists/{gist_id}` | 删除 Gist |
| 196 | Star Gist | `PUT` | `gists/{gist_id}/star` | Star Gist |
| 197 | 列出 Gist 评论 | `GET` | `gists/{gist_id}/comments` | 列出 Gist 评论 |
| 198 | 创建 Gist 评论 | `POST` | `gists/{gist_id}/comments` | 创建 Gist 评论 |

### Deployments（8 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 199 | 列出 Deployments | `GET` | `repos/{owner}/{repo}/deployments` | 列出仓库 Deployment |
| 200 | 获取 Deployment | `GET` | `repos/{owner}/{repo}/deployments/{deployment_id}` | 获取 Deployment 详情 |
| 201 | 创建 Deployment | `POST` | `repos/{owner}/{repo}/deployments` | 创建 Deployment |
| 202 | 删除 Deployment | `DELETE` | `repos/{owner}/{repo}/deployments/{deployment_id}` | 删除 Deployment |
| 203 | 列出 Deployment Statuses | `GET` | `repos/{owner}/{repo}/deployments/{deployment_id}/statuses` | 列出 Deployment 状态 |
| 204 | 获取 Deployment Status | `GET` | `repos/{owner}/{repo}/deployments/{deployment_id}/statuses/{status_id}` | 获取状态详情 |
| 205 | 创建 Deployment Status | `POST` | `repos/{owner}/{repo}/deployments/{deployment_id}/statuses` | 更新 Deployment 状态 |
| 206 | 列出 Environments | `GET` | `repos/{owner}/{repo}/environments` | 列出仓库 Environments |

---

## §5 策略指南

### 5.1 意图→接口决策树

根据用户意图，快速定位推荐接口：

| 用户意图 | 推荐接口 | 备注 |
|----------|----------|------|
| 查看 Issue 列表 | #1 `GET repos/{owner}/{repo}/issues` | 用 `state=open/closed/all` 过滤；注意此接口也返回 PR |
| 创建 Issue | #3 `POST repos/{owner}/{repo}/issues` | 可同时设置 labels/assignees/milestone |
| 关闭/重新打开 Issue | #4 `PATCH repos/{owner}/{repo}/issues/{n}` | `state: "closed"` 或 `state: "open"` |
| 评论 Issue | #9 `POST repos/{owner}/{repo}/issues/{n}/comments` | PR 的非代码评论也用此接口 |
| 管理标签 | #18 `POST .../labels` / #19 `DELETE .../labels/{name}` | 批量添加用 POST 传数组；移除需逐个 DELETE |
| 分配人员 | #21 `POST .../assignees` | body: `{"assignees": ["user1","user2"]}` |
| 查看 PR 列表 | #26 `GET repos/{owner}/{repo}/pulls` | 用 `state=open/closed/all` 过滤 |
| 创建 PR | #28 `POST repos/{owner}/{repo}/pulls` | 需指定 head（源分支）和 base（目标分支） |
| 检查 PR 可否合并 | #27 `GET repos/{owner}/{repo}/pulls/{n}` | 检查 `mergeable` 和 `mergeable_state` 字段 |
| 合并 PR | workflow:merge-pr | 先检查 mergeable → 再 PUT merge；见 §5.2 |
| 查看 PR 变更文件 | #31 `GET .../pulls/{n}/files` | 返回 filename/status/additions/deletions/patch |
| 审查 PR | #38 `POST .../pulls/{n}/reviews` | event: APPROVE/REQUEST_CHANGES/COMMENT |
| 获取仓库信息 | #46 `GET repos/{owner}/{repo}` | 返回完整仓库元数据 |
| 创建仓库 | #49 `POST user/repos` | 组织仓库用 #50 `POST orgs/{org}/repos` |
| Fork 仓库 | #53 `POST repos/{owner}/{repo}/forks` | 可指定 organization 和 name |
| 读取文件内容 | #55 `GET repos/{owner}/{repo}/contents/{path}` | 返回 base64 编码内容；目录返回文件列表 |
| 更新文件 | workflow:update-file | 先 GET 获取 SHA → 再 PUT 带 SHA；见 §5.2 |
| 创建 Release | #65 `POST repos/{owner}/{repo}/releases` | 需指定 tag_name；可自动从 tag 创建 |
| 上传 Release 附件 | workflow:upload-release-asset | 用 uploads.github.com 域名；见 §5.2 |
| 搜索仓库 | #96 `GET search/repositories` | q 参数支持 `language:go stars:>100` 等限定词 |
| 搜索 Issue/PR | #97 `GET search/issues` | q 参数支持 `is:issue is:open repo:owner/repo` 等 |
| 搜索代码 | #98 `GET search/code` | q 参数支持 `filename:*.go path:src/` 等 |
| 搜索后操作 | workflow:search-then-act | 搜索 → 提取 ID → 调用操作接口；见 §5.2 |
| 获取当前用户 | #84 `GET user` | 确认认证身份 |
| 查看用户资料 | #86 `GET users/{username}` | 公开信息，无需特殊权限 |
| 查看 Workflow 列表 | #102 `GET .../actions/workflows` | 返回 workflow 文件名和 ID |
| 触发 Workflow | workflow:trigger-workflow | dispatch → 等待 → poll；见 §5.2 |
| 查看 Run 状态 | #107 `GET .../actions/runs/{run_id}` | 返回 status/conclusion |
| 取消运行中的 Run | #108 `POST .../actions/runs/{run_id}/cancel` | 仅对 in_progress/queued 有效 |
| 重新运行 | #109 `POST .../actions/runs/{run_id}/rerun` | 重新运行全部 Job |
| 管理 Secrets | #124 `PUT .../actions/secrets/{name}` | 需先获取 public key 并加密 |
| 管理 Variables | #129 `POST .../actions/variables` | 直接传明文值（不需要加密） |
| 查看组织信息 | #137 `GET orgs/{org}` | 公开信息 |
| 查看组织成员 | #140 `GET orgs/{org}/members` | 需组织访问权限 |
| 管理团队 | #146 `POST orgs/{org}/teams` | 创建/管理团队需 admin 权限 |
| 查看 Commit 详情 | #156 `GET repos/{owner}/{repo}/commits/{ref}` | 含文件变更列表 |
| 比较两个 Commit | #157 `GET .../compare/{base}...{head}` | 返回 diff 和文件变更 |
| 查看 Check Run 状态 | #160 `GET .../commits/{ref}/check-runs` | CI/CD 检查结果 |
| 创建 Commit Status | #166 `POST .../statuses/{sha}` | state: pending/success/error/failure |
| 查看通知 | #169 `GET notifications` | 认证用户的通知收件箱 |
| 标记通知已读 | #171 `PUT notifications` | 标记所有为已读 |
| Star 仓库 | #175 `PUT user/starred/{owner}/{repo}` | 返回 204 |
| Watch 仓库 | #178 `PUT .../subscription` | 设置订阅级别 |
| 通过 API 创建 Commit | workflow:create-commit-via-api | blob→tree→commit→ref 5 步；见 §5.2 |
| 创建/管理 Gist | #193 `POST gists` | 支持多文件 |
| 创建 Deployment | #201 `POST .../deployments` | 触发部署流程 |
| 更新 Deployment 状态 | #205 `POST .../deployments/{id}/statuses` | state: success/failure/error/inactive 等 |

### 5.2 命名工作流

#### workflow:merge-pr（合并 PR）

```
步骤 1 → #27 GET repos/{owner}/{repo}/pulls/{pull_number}
         — 检查 mergeable == true 且 mergeable_state == "clean"
         — 如果 mergeable 为 null，等待 3-5 秒后重试（GitHub 正在计算）
步骤 2 → #30 PUT repos/{owner}/{repo}/pulls/{pull_number}/merge
         — merge_method: "merge" / "squash" / "rebase"（按用户偏好）
         — ⚠️ 执行前向用户确认
```

> 如果 `mergeable_state` 不是 "clean"（如 "blocked"/"behind"/"dirty"），向用户报告原因，不要强行合并。

#### workflow:update-file（更新文件内容）

```
步骤 1 → #55 GET repos/{owner}/{repo}/contents/{path}
         — 提取 response.sha（当前文件的 blob SHA）
步骤 2 → #56 PUT repos/{owner}/{repo}/contents/{path}
         — 必须携带 sha（步骤 1 获取的值）
         — content: base64 编码的新文件内容
         — message: commit message
```

> **关键**：不带 sha 的 PUT 会返回 422 错误。如果是新建文件（步骤 1 返回 404），则不需要 sha。

#### workflow:upload-release-asset（上传 Release 资产）

```
步骤 1 → #65 POST repos/{owner}/{repo}/releases（如果 Release 不存在）
         — 或 #62 GET releases/{release_id}（获取已有 Release 的 upload_url）
步骤 2 → #69 POST {upload_url}?name={filename}
         — ⚠️ 注意：upload_url 域名是 uploads.github.com（不是 api.github.com）
         — Content-Type: 按文件类型设置（如 application/zip, application/octet-stream）
         — Body: 文件二进制内容（不是 JSON）
```

> `upload_url` 从 Release 对象的 `upload_url` 字段获取，已包含完整 URL（需替换 `{?name,label}` 部分）。

#### workflow:search-then-act（搜索后操作）

```
步骤 1 → #96-#101 GET search/{type}?q={query}&per_page=100
         — 搜索目标实体（repo/issue/code/commit/user）
步骤 2 → 从 response.items 中提取目标 ID/URL
步骤 3 → 调用对应操作接口（如 #4 更新 Issue、#29 更新 PR 等）
```

> Search 限流独立（30 req/min），批量搜索时注意间隔。结果最多 1,000 条。

#### workflow:trigger-workflow（触发 Workflow 并追踪）

```
步骤 1 → #102 GET repos/{owner}/{repo}/actions/workflows
         — 找到目标 Workflow 的 ID（或直接使用文件名如 ci.yml）
步骤 2 → #105 GET repos/{owner}/{repo}/actions/runs?per_page=1
         — 记录当前最新 run_id 作为基线（用于后续识别新 Run）
步骤 3 → #104 POST repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches
         — body: {"ref": "main", "inputs": {...}}
         — ⚠️ 执行前向用户确认（消耗 Actions 分钟数）
         — 成功返回 204（无 body）
步骤 4 → 等待 3-5 秒后轮询:
         #106 GET repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs?per_page=5
         — 找到 run_id > 基线的新 Run
步骤 5 → #107 GET repos/{owner}/{repo}/actions/runs/{new_run_id}
         — 轮询 status 直到不再是 "queued"/"in_progress"
         — 间隔 10-15 秒，最多轮询 20 次
```

> dispatch 返回 204 但不返回 run_id，因此需要通过基线比较来识别新 Run。

#### workflow:create-commit-via-api（无需本地 git 提交代码）

```
步骤 1 → #187 GET repos/{owner}/{repo}/git/ref/heads/{branch}
         — 获取当前分支的 commit SHA
步骤 2 → #186 GET repos/{owner}/{repo}/git/commits/{commit_sha}
         — 获取当前 commit 的 tree SHA
步骤 3 → #181 POST repos/{owner}/{repo}/git/blobs
         — 为每个要创建/修改的文件创建 blob
         — body: {"content": "文件内容", "encoding": "utf-8"}
步骤 4 → #183 POST repos/{owner}/{repo}/git/trees
         — 创建新 tree，base_tree 为步骤 2 的 tree SHA
         — body: {"base_tree": "TREE_SHA", "tree": [{"path": "file.txt", "mode": "100644", "type": "blob", "sha": "BLOB_SHA"}]}
步骤 5 → #185 POST repos/{owner}/{repo}/git/commits
         — 创建新 commit，parent 为步骤 1 的 commit SHA
         — body: {"message": "commit message", "tree": "NEW_TREE_SHA", "parents": ["PARENT_SHA"]}
步骤 6 → #189 PATCH repos/{owner}/{repo}/git/refs/heads/{branch}
         — 更新分支指向新 commit
         — body: {"sha": "NEW_COMMIT_SHA"}
```

> 此流程允许在无本地 git 环境的情况下通过 API 提交代码变更。适合 AI 代理远程操作。

---

## §6 Shell 格式模板

所有操作速查以 bash 为主要示例格式。PowerShell 转换遵循以下统一规则，不在每个接口处重复说明。

### 6.1 基础结构对比表

| 要素 | bash | PowerShell |
|------|------|------------|
| Token 获取 | `$(bash '<SCRIPT_PATH>/get-token.sh')` 内联在命令中 | `$token = & "<SCRIPT_PATH>\get-token.ps1"` 先获取再引用 `$token` |
| GET 请求 | `curl -s "URL" -H "Key: Value"` | `irm "URL" -Headers @{"Key"="Value"}` |
| POST/PATCH/PUT 请求 | `curl -s -X METHOD "URL" -H "..." -d '{...}'` | `$body = @{...} \| ConvertTo-Json -Depth 10; irm "URL" -Method Method -Headers @{...} -ContentType "application/json" -Body $body` |
| DELETE 请求 | `curl -s -X DELETE "URL" -H "..."` | `irm "URL" -Method Delete -Headers @{...}` |
| 文件上传（binary） | `curl -s -X POST "URL" -H "Content-Type: ..." --data-binary @path` | `curl.exe -s -X POST "URL" -H "..." --data-binary @path`（irm 不便处理 binary upload） |
| 续行符 | `\` | `` ` ``（反引号） |
| Header 格式 | `-H "Key: Value"` | `-Headers @{"Key"="Value"}` |

### 6.2 完整模板

**bash 模板**
```bash
# GET 请求模板
curl -s "https://api.github.com/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"

# POST/PATCH/PUT 请求模板
curl -s -X {{METHOD}} "https://api.github.com/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{{BODY}}'

# DELETE 请求模板
curl -s -X DELETE "https://api.github.com/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

**PowerShell 模板**
```powershell
# GET 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
irm "https://api.github.com/{{PATH}}" `
  -Headers @{"Authorization"="Bearer $token"; "X-GitHub-Api-Version"="2022-11-28"; "Accept"="application/vnd.github+json"}

# POST/PATCH/PUT 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
$body = @{ {{BODY}} } | ConvertTo-Json -Depth 10
irm "https://api.github.com/{{PATH}}" -Method {{METHOD}} `
  -Headers @{"Authorization"="Bearer $token"; "X-GitHub-Api-Version"="2022-11-28"; "Accept"="application/vnd.github+json"} `
  -ContentType "application/json" -Body $body

# DELETE 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
irm "https://api.github.com/{{PATH}}" -Method Delete `
  -Headers @{"Authorization"="Bearer $token"; "X-GitHub-Api-Version"="2022-11-28"; "Accept"="application/vnd.github+json"}
```

### 6.3 转换规则摘要

从 bash 示例转换为 PowerShell 的步骤：

1. **Token**：将 `$(bash '<SCRIPT_PATH>/get-token.sh')` 替换为先执行 `$token = & "<SCRIPT_PATH>\get-token.ps1"` 再在 Header 中使用 `$token`
2. **命令**：将 `curl -s` 替换为 `irm`，`-X METHOD` 替换为 `-Method Method`
3. **Header**：将 `-H "Key: Value"` 替换为 `-Headers @{"Key"="Value"}`
4. **Body**：将 `-d '{...}'` 替换为 `$body = @{...} | ConvertTo-Json -Depth 10` + `-Body $body`
5. **续行**：将 `\` 替换为 `` ` ``；文件上传场景改用 `curl.exe` 而非 `irm`
6. **Accept Header**：始终包含 `Accept: application/vnd.github+json`（GitHub API 推荐）

---

## §7 接口详情

> 所有示例以 bash 为主。PowerShell 转换规则见 [§6 Shell 格式模板](#6-shell-格式模板)，不在每个接口处重复。
> `<SCRIPT_PATH>` 在初始化阶段替换为本文件所在目录的绝对路径。

---

### Issues 操作（#1-#25）

#### 1. 列出仓库 Issue

`GET repos/{owner}/{repo}/issues`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |
| state | query | — | `open`/`closed`/`all`（默认 open） |
| labels | query | — | 逗号分隔的标签名（如 `bug,help wanted`） |
| assignee | query | — | 用户名（`*` = 任何已分配，`none` = 未分配） |
| sort | query | — | `created`/`updated`/`comments`（默认 created） |
| direction | query | — | `asc`/`desc`（默认 desc） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/issues?state=open&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> **注意**：此接口同时返回 Issue 和 PR。纯 Issue 过滤：排除含 `pull_request` 字段的项。

#### 2. 获取 Issue

`GET repos/{owner}/{repo}/issues/{issue_number}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |
| issue_number | path | ✅ | Issue 编号 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 3. 创建 Issue

`POST repos/{owner}/{repo}/issues`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |
| title | body | ✅ | Issue 标题 |
| body | body | — | Issue 内容（Markdown） |
| labels | body | — | 标签数组 `["bug","help wanted"]` |
| assignees | body | — | 分配人数组 `["user1"]` |
| milestone | body | — | 里程碑编号（整数） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Issue 标题",
    "body": "Issue 描述内容",
    "labels": ["bug"],
    "assignees": ["username"]
  }'
```

#### 4. 更新 Issue

`PATCH repos/{owner}/{repo}/issues/{issue_number}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| issue_number | path | ✅ | Issue 编号 |
| title | body | — | 新标题 |
| body | body | — | 新内容 |
| state | body | — | `open`/`closed` |
| state_reason | body | — | `completed`/`not_planned`/`reopened` |
| labels | body | — | 替换全部标签 |
| assignees | body | — | 替换全部分配人 |

```bash
curl -s -X PATCH "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"state": "closed", "state_reason": "completed"}'
```

#### 5. 锁定 Issue

`PUT repos/{owner}/{repo}/issues/{issue_number}/lock`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| lock_reason | body | — | `off-topic`/`too heated`/`resolved`/`spam` |

```bash
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/lock" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"lock_reason": "resolved"}'
```

#### 9. 创建 Issue 评论

`POST repos/{owner}/{repo}/issues/{issue_number}/comments`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| issue_number | path | ✅ | Issue 编号（也适用于 PR 编号） |
| body | body | ✅ | 评论内容（Markdown） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/comments" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"body": "评论内容"}'
```

#### 14. 创建标签

`POST repos/{owner}/{repo}/labels`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | 标签名 |
| color | body | ✅ | 颜色（6 位 hex，不带 #，如 `ff0000`） |
| description | body | — | 标签描述 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/labels" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"name": "priority-high", "color": "ff0000", "description": "高优先级"}'
```

#### 18. 添加 Issue 标签

`POST repos/{owner}/{repo}/issues/{issue_number}/labels`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| labels | body | ✅ | 标签名数组 `["bug","help wanted"]` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/labels" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"labels": ["bug", "help wanted"]}'
```

#### 21. 添加 Assignees

`POST repos/{owner}/{repo}/issues/{issue_number}/assignees`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| assignees | body | ✅ | 用户名数组 `["user1","user2"]` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/assignees" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"assignees": ["username"]}'
```

---

### Pull Requests 操作（#26-#45）

#### 26. 列出 PR

`GET repos/{owner}/{repo}/pulls`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| state | query | — | `open`/`closed`/`all`（默认 open） |
| head | query | — | 过滤源分支（格式 `user:branch`） |
| base | query | — | 过滤目标分支 |
| sort | query | — | `created`/`updated`/`popularity`/`long-running` |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/pulls?state=open&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 27. 获取 PR

`GET repos/{owner}/{repo}/pulls/{pull_number}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| pull_number | path | ✅ | PR 编号 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `mergeable`（bool/null）和 `mergeable_state`（"clean"/"dirty"/"blocked"/"behind"/"unknown"）。`mergeable` 为 null 表示 GitHub 正在计算，需等待重试。

#### 28. 创建 PR

`POST repos/{owner}/{repo}/pulls`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| title | body | ✅ | PR 标题 |
| head | body | ✅ | 源分支（或 `user:branch` 跨 fork） |
| base | body | ✅ | 目标分支 |
| body | body | — | PR 描述（Markdown） |
| draft | body | — | 是否为草稿 PR |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/pulls" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "PR 标题",
    "head": "feature-branch",
    "base": "main",
    "body": "PR 描述"
  }'
```

#### 30. 合并 PR ⚠️ DESTRUCTIVE

`PUT repos/{owner}/{repo}/pulls/{pull_number}/merge`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| commit_title | body | — | 合并 commit 标题 |
| commit_message | body | — | 合并 commit 描述 |
| merge_method | body | — | `merge`/`squash`/`rebase` |
| sha | body | — | PR HEAD SHA（确保合并时 PR 未变更） |

```bash
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/merge" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"merge_method": "squash", "commit_title": "feat: 新功能"}'
```

#### 31. 列出 PR 文件

`GET repos/{owner}/{repo}/pulls/{pull_number}/files`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/files?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 38. 创建 PR Review

`POST repos/{owner}/{repo}/pulls/{pull_number}/reviews`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| event | body | ✅ | `APPROVE`/`REQUEST_CHANGES`/`COMMENT` |
| body | body | — | Review 总结评论 |
| comments | body | — | 行内评论数组 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/reviews" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"event": "APPROVE", "body": "LGTM!"}'
```

#### 42. 请求 Review

`POST repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| reviewers | body | — | 用户名数组 |
| team_reviewers | body | — | 团队 slug 数组 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/requested_reviewers" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"reviewers": ["reviewer-username"]}'
```

---

### Repos 操作（#46-#83）

#### 46. 获取仓库

`GET repos/{owner}/{repo}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 49. 创建仓库

`POST user/repos`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | 仓库名 |
| description | body | — | 仓库描述 |
| private | body | — | 是否私有（默认 false） |
| auto_init | body | — | 是否自动初始化 README |
| gitignore_template | body | — | .gitignore 模板（如 `Go`/`Node`） |
| license_template | body | — | License 模板（如 `mit`/`apache-2.0`） |

```bash
curl -s -X POST "https://api.github.com/user/repos" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-repo",
    "description": "仓库描述",
    "private": false,
    "auto_init": true
  }'
```

#### 53. Fork 仓库

`POST repos/{owner}/{repo}/forks`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| organization | body | — | Fork 到指定组织（默认当前用户） |
| name | body | — | 自定义 Fork 名称 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/forks" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 55. 获取文件内容

`GET repos/{owner}/{repo}/contents/{path}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| path | path | ✅ | 文件路径（如 `src/main.go`） |
| ref | query | — | 分支/tag/commit SHA（默认默认分支） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/contents/README.md" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `content`（base64 编码）和 `sha`。解码内容：`echo "$content" | base64 -d`。目录返回文件对象数组。

#### 56. 创建/更新文件

`PUT repos/{owner}/{repo}/contents/{path}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| path | path | ✅ | 文件路径 |
| message | body | ✅ | Commit message |
| content | body | ✅ | base64 编码的文件内容 |
| sha | body | ⚠️ | 更新已有文件时**必填**（从 GET 获取） |
| branch | body | — | 目标分支（默认默认分支） |

```bash
# 更新已有文件（需要 sha）
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/contents/path/to/file.txt" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "更新文件",
    "content": "SGVsbG8gV29ybGQ=",
    "sha": "CURRENT_FILE_SHA"
  }'
```

#### 61. 列出 Release

`GET repos/{owner}/{repo}/releases`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/releases?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 65. 创建 Release

`POST repos/{owner}/{repo}/releases`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| tag_name | body | ✅ | Tag 名（如 `v1.0.0`） |
| name | body | — | Release 标题 |
| body | body | — | Release 说明（Markdown） |
| draft | body | — | 是否为草稿 |
| prerelease | body | — | 是否为预发布 |
| target_commitish | body | — | 创建 Tag 的目标（branch/SHA） |
| generate_release_notes | body | — | 自动生成 Release Notes |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/releases" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "tag_name": "v1.0.0",
    "name": "Release v1.0.0",
    "body": "## 变更内容\n- 新功能",
    "generate_release_notes": true
  }'
```

#### 69. 上传 Release Asset

`POST uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| release_id | path | ✅ | Release ID |
| name | query | ✅ | 文件名 |
| label | query | — | 显示标签 |
| Content-Type | header | ✅ | 文件 MIME 类型 |

```bash
curl -s -X POST "https://uploads.github.com/repos/OWNER/REPO/releases/RELEASE_ID/assets?name=app.zip" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/zip" \
  --data-binary @app.zip
```

> **注意**：域名是 `uploads.github.com`（不是 `api.github.com`），Content-Type 按文件实际类型设置。

---

### Users 操作（#84-#95）

#### 84. 获取认证用户

`GET user`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| — | — | — | 无参数 |

```bash
curl -s "https://api.github.com/user" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 86. 获取用户

`GET users/{username}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| username | path | ✅ | 用户名 |

```bash
curl -s "https://api.github.com/users/USERNAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 90. 关注用户

`PUT user/following/{username}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| username | path | ✅ | 要关注的用户名 |

```bash
curl -s -X PUT "https://api.github.com/user/following/USERNAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 成功返回 204（无 body）。

#### 93. 添加 SSH Key

`POST user/keys`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| title | body | ✅ | Key 标题 |
| key | body | ✅ | SSH 公钥内容 |

```bash
curl -s -X POST "https://api.github.com/user/keys" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"title": "My SSH Key", "key": "ssh-ed25519 AAAA..."}'
```

---

### Search 操作（#96-#101）

> **限流提醒**：Search API 独立限流 30 req/min（见 §8.5）。批量搜索时注意间隔。

#### 96. 搜索仓库

`GET search/repositories`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（支持限定词：`language:go stars:>100 topic:cli`） |
| sort | query | — | `stars`/`forks`/`help-wanted-issues`/`updated` |
| order | query | — | `asc`/`desc` |
| per_page | query | — | 每页数量（最大 100） |

```bash
curl -s "https://api.github.com/search/repositories?q=language:go+stars:>1000&sort=stars&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `total_count` + `items` 数组。`items` 中每个对象含 `full_name`、`html_url`、`description` 等。

#### 97. 搜索 Issues/PRs

`GET search/issues`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`is:issue is:open repo:owner/repo label:bug`） |
| sort | query | — | `comments`/`reactions`/`created`/`updated` |
| order | query | — | `asc`/`desc` |
| per_page | query | — | 每页数量（最大 100） |

```bash
curl -s "https://api.github.com/search/issues?q=is:issue+is:open+repo:cli/cli+label:bug&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> **常用限定词**：`is:issue`/`is:pr`、`is:open`/`is:closed`、`repo:owner/repo`、`author:user`、`label:name`、`assignee:user`。

#### 98. 搜索代码

`GET search/code`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`filename:*.go repo:owner/repo path:src/`） |
| sort | query | — | `indexed`（按索引日期） |
| order | query | — | `asc`/`desc` |
| per_page | query | — | 每页数量（最大 100） |

```bash
curl -s "https://api.github.com/search/code?q=handleError+repo:cli/cli+filename:*.go&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 代码搜索**必须**指定 `repo:`、`org:` 或 `user:` 限定词，否则返回 422。

#### 99. 搜索 Commits

`GET search/commits`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`repo:owner/repo author:user`） |
| sort | query | — | `author-date`/`committer-date` |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/search/commits?q=fix+repo:cli/cli&sort=author-date&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 100. 搜索用户

`GET search/users`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`type:user location:china language:go`） |
| sort | query | — | `followers`/`repositories`/`joined` |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/search/users?q=type:user+language:go+followers:>100&sort=followers&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 101. 搜索 Topics

`GET search/topics`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | Topic 名称关键词 |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/search/topics?q=machine-learning&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

---

### Actions 操作（#102-#136）

#### 102. 列出仓库 Workflows

`GET repos/{owner}/{repo}/actions/workflows`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/workflows?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 104. 触发 Workflow ⚠️ DESTRUCTIVE

`POST repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| workflow_id | path | ✅ | Workflow ID 或文件名（如 `ci.yml`） |
| ref | body | ✅ | 目标分支/tag |
| inputs | body | — | Workflow 输入参数（key-value 对象） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/workflows/ci.yml/dispatches" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"ref": "main", "inputs": {"environment": "staging"}}'
```

> 成功返回 204（无 body）。不返回 run_id，需通过 workflow:trigger-workflow 流程追踪。

#### 105. 列出 Workflow Runs

`GET repos/{owner}/{repo}/actions/runs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| status | query | — | `completed`/`in_progress`/`queued`/`waiting` 等 |
| branch | query | — | 过滤分支 |
| event | query | — | 触发事件（`push`/`pull_request`/`workflow_dispatch` 等） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs?status=completed&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 107. 获取 Run

`GET repos/{owner}/{repo}/actions/runs/{run_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| run_id | path | ✅ | Run ID |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 关键字段：`status`（queued/in_progress/completed）、`conclusion`（success/failure/cancelled/skipped）。

#### 108. 取消 Run

`POST repos/{owner}/{repo}/actions/runs/{run_id}/cancel`

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/cancel" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 109. 重新运行 Run

`POST repos/{owner}/{repo}/actions/runs/{run_id}/rerun`

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/rerun" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 114. 列出 Run 的 Jobs

`GET repos/{owner}/{repo}/actions/runs/{run_id}/jobs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| filter | query | — | `latest`（仅最新尝试）/`all` |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/jobs?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 120. 下载 Artifact

`GET repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip`

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID/zip" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -o artifact.zip
```

> 返回 302 重定向到下载 URL，使用 `-L` 跟随重定向。

#### 124. 创建/更新 Secret（需加密）

`PUT repos/{owner}/{repo}/actions/secrets/{secret_name}`

**加密流程**（必须先获取 public key）：

```bash
# 步骤 1：获取仓库 public key
curl -s "https://api.github.com/repos/OWNER/REPO/actions/secrets/public-key" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
# 返回：{"key_id": "...", "key": "base64_public_key"}

# 步骤 2：使用 openssl 加密 Secret（无需 libsodium）
# 注意：GitHub 使用 libsodium sealed box 加密，openssl 不能直接替代
# 推荐方式：使用 Python 或 Node.js 的 tweetnacl 库
python3 -c "
import base64, sys
from nacl.public import SealedBox, PublicKey
public_key = base64.b64decode('BASE64_PUBLIC_KEY')
sealed_box = SealedBox(PublicKey(public_key))
encrypted = sealed_box.encrypt(b'SECRET_VALUE')
print(base64.b64encode(encrypted).decode())
"

# 步骤 3：创建/更新 Secret
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/actions/secrets/MY_SECRET" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"encrypted_value": "ENCRYPTED_BASE64", "key_id": "KEY_ID"}'
```

> Secret 值必须使用 libsodium sealed box 加密。Python `pynacl` 或 Node.js `tweetnacl` 均可完成。

#### 129. 创建 Variable

`POST repos/{owner}/{repo}/actions/variables`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | Variable 名称 |
| value | body | ✅ | Variable 值（明文） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/variables" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"name": "ENV_NAME", "value": "production"}'
```

---

### Orgs & Teams 操作（#137-#154）

#### 137. 获取组织

`GET orgs/{org}`

```bash
curl -s "https://api.github.com/orgs/ORG_NAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 140. 列出组织成员

`GET orgs/{org}/members`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| role | query | — | `all`/`admin`/`member`（默认 all） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/orgs/ORG_NAME/members?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 146. 创建团队

`POST orgs/{org}/teams`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | 团队名称 |
| description | body | — | 团队描述 |
| privacy | body | — | `secret`（仅成员可见）/`closed`（组织内可见） |
| permission | body | — | `pull`/`push`/`admin` |

```bash
curl -s -X POST "https://api.github.com/orgs/ORG_NAME/teams" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"name": "frontend-team", "description": "前端团队", "privacy": "closed"}'
```

#### 150. 添加团队成员

`PUT orgs/{org}/teams/{team_slug}/memberships/{username}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| role | body | — | `member`/`maintainer`（默认 member） |

```bash
curl -s -X PUT "https://api.github.com/orgs/ORG_NAME/teams/TEAM_SLUG/memberships/USERNAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"role": "member"}'
```

---

### Commits & Checks 操作（#155-#168）

#### 155. 列出 Commits

`GET repos/{owner}/{repo}/commits`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| sha | query | — | 分支名或 commit SHA |
| path | query | — | 过滤修改了指定路径的 commit |
| author | query | — | 过滤作者（GitHub 用户名或邮箱） |
| since | query | — | 起始时间（ISO 8601） |
| until | query | — | 截止时间（ISO 8601） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits?sha=main&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 156. 获取 Commit

`GET repos/{owner}/{repo}/commits/{ref}`

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits/COMMIT_SHA" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `files` 数组含每个变更文件的 filename/status/additions/deletions/patch。

#### 157. 比较 Commits

`GET repos/{owner}/{repo}/compare/{basehead}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| basehead | path | ✅ | 格式 `base...head`（如 `main...feature`） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/compare/main...feature-branch" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 160. 列出 Commit 的 Check Runs

`GET repos/{owner}/{repo}/commits/{ref}/check-runs`

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits/COMMIT_SHA/check-runs?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 164. 获取 Combined Status

`GET repos/{owner}/{repo}/commits/{ref}/status`

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits/COMMIT_SHA/status" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `state`（pending/success/error/failure）和 `statuses` 数组。

#### 166. 创建 Commit Status

`POST repos/{owner}/{repo}/statuses/{sha}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| sha | path | ✅ | Commit SHA |
| state | body | ✅ | `pending`/`success`/`error`/`failure` |
| target_url | body | — | 状态详情链接 |
| description | body | — | 状态描述 |
| context | body | — | 状态上下文标识（如 `ci/build`） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/statuses/COMMIT_SHA" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "success",
    "target_url": "https://ci.example.com/build/123",
    "description": "Build passed",
    "context": "ci/build"
  }'
```

---

### Activity 操作（#169-#180）

#### 169. 列出通知

`GET notifications`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| all | query | — | `true` 包含已读通知 |
| participating | query | — | `true` 仅参与的 |
| since | query | — | 起始时间（ISO 8601） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/notifications?all=false&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 171. 标记通知已读

`PUT notifications`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| last_read_at | body | — | 标记此时间之前的通知为已读（ISO 8601，默认当前时间） |

```bash
curl -s -X PUT "https://api.github.com/notifications" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"last_read_at": "2024-01-01T00:00:00Z"}'
```

#### 175. Star 仓库

`PUT user/starred/{owner}/{repo}`

```bash
curl -s -X PUT "https://api.github.com/user/starred/OWNER/REPO" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 成功返回 204（无 body）。

#### 177. 列出用户 Starred

`GET users/{username}/starred`

```bash
curl -s "https://api.github.com/users/USERNAME/starred?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 178. Watch 仓库

`PUT repos/{owner}/{repo}/subscription`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| subscribed | body | — | 是否订阅通知 |
| ignored | body | — | 是否忽略通知 |

```bash
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/subscription" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"subscribed": true, "ignored": false}'
```

---

### Git Low-level 操作（#181-#190）

#### 181. 创建 Blob

`POST repos/{owner}/{repo}/git/blobs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| content | body | ✅ | 文件内容 |
| encoding | body | — | `utf-8`（默认）或 `base64` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/blobs" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"content": "文件内容", "encoding": "utf-8"}'
```

#### 183. 创建 Tree

`POST repos/{owner}/{repo}/git/trees`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| tree | body | ✅ | Tree 条目数组 |
| base_tree | body | — | 基础 tree SHA（增量更新时使用） |

每个 tree 条目：

| 字段 | 必填 | 说明 |
|------|------|------|
| path | ✅ | 文件路径 |
| mode | ✅ | `100644`（普通文件）/`100755`（可执行）/`040000`（目录）/`160000`（子模块） |
| type | ✅ | `blob`/`tree`/`commit` |
| sha | ⚠️ | Blob SHA（与 content 二选一） |
| content | ⚠️ | 直接内联内容（与 sha 二选一） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/trees" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "base_tree": "BASE_TREE_SHA",
    "tree": [
      {"path": "src/main.go", "mode": "100644", "type": "blob", "sha": "BLOB_SHA"}
    ]
  }'
```

#### 185. 创建 Commit

`POST repos/{owner}/{repo}/git/commits`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| message | body | ✅ | Commit message |
| tree | body | ✅ | Tree SHA |
| parents | body | ✅ | 父 commit SHA 数组 |
| author | body | — | 作者信息 `{name, email, date}` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/commits" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "feat: 通过 API 创建的 commit",
    "tree": "NEW_TREE_SHA",
    "parents": ["PARENT_COMMIT_SHA"]
  }'
```

#### 187. 获取 Ref

`GET repos/{owner}/{repo}/git/ref/{ref}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | path | ✅ | Ref 路径（如 `heads/main`、`tags/v1.0`） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/git/ref/heads/main" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `object.sha` 即为当前分支指向的 commit SHA。

#### 188. 创建 Ref

`POST repos/{owner}/{repo}/git/refs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | body | ✅ | Ref 全路径（如 `refs/heads/new-branch`） |
| sha | body | ✅ | 指向的 commit SHA |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/refs" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"ref": "refs/heads/new-branch", "sha": "COMMIT_SHA"}'
```

#### 189. 更新 Ref

`PATCH repos/{owner}/{repo}/git/refs/{ref}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | path | ✅ | Ref 路径（如 `heads/main`） |
| sha | body | ✅ | 新指向的 commit SHA |
| force | body | — | 是否强制更新（非 fast-forward） |

```bash
curl -s -X PATCH "https://api.github.com/repos/OWNER/REPO/git/refs/heads/main" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"sha": "NEW_COMMIT_SHA"}'
```

---

### Gists 操作（#191-#198）

#### 193. 创建 Gist

`POST gists`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| files | body | ✅ | 文件对象 `{"filename": {"content": "..."}}` |
| description | body | — | Gist 描述 |
| public | body | — | 是否公开（默认 false） |

```bash
curl -s -X POST "https://api.github.com/gists" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "代码片段",
    "public": false,
    "files": {
      "hello.py": {"content": "print(\"Hello World\")"}
    }
  }'
```

#### 194. 更新 Gist

`PATCH gists/{gist_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| files | body | — | 文件变更（content=null 删除文件，新 key 添加文件） |
| description | body | — | 新描述 |

```bash
curl -s -X PATCH "https://api.github.com/gists/GIST_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "files": {
      "hello.py": {"content": "print(\"Updated\")"},
      "new_file.txt": {"content": "新文件内容"}
    }
  }'
```

---

### Deployments 操作（#199-#206）

#### 201. 创建 Deployment

`POST repos/{owner}/{repo}/deployments`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | body | ✅ | 部署的分支/tag/SHA |
| environment | body | — | 环境名（如 `production`/`staging`） |
| description | body | — | 部署描述 |
| auto_merge | body | — | 是否自动合并（默认 true） |
| required_contexts | body | — | 必须通过的状态检查（空数组跳过检查） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/deployments" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "main",
    "environment": "production",
    "description": "部署到生产环境",
    "required_contexts": []
  }'
```

#### 205. 创建 Deployment Status

`POST repos/{owner}/{repo}/deployments/{deployment_id}/statuses`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| state | body | ✅ | `error`/`failure`/`inactive`/`in_progress`/`queued`/`pending`/`success` |
| description | body | — | 状态描述 |
| environment_url | body | — | 环境 URL |
| log_url | body | — | 日志 URL |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/deployments/DEPLOYMENT_ID/statuses" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "success",
    "description": "部署成功",
    "environment_url": "https://app.example.com"
  }'
```

---

## §8 运维契约

### 8.1 HTTP 错误→AI 行为映射表

收到 API 错误时，AI 必须按以下表格执行对应行为：

| HTTP 状态码 | 含义 | AI 行为 |
|------------|------|---------|
| 400 | Bad Request | 检查请求体 JSON 语法和必填参数，对照 §7 参数表修正后重试 |
| 401 | Unauthorized / Bad credentials | 提示用户检查 Token 是否有效或已过期；**绝不在输出中显示 Token 值** |
| 403（body 含 "secondary rate limit"） | 次级限流 | 执行限流处理算法（见 §8.3），等待 `retry-after` 或指数退避后重试 |
| 403（body 含 "Resource not accessible"） | 权限不足 | 告知用户：当前 Token 无权执行此操作。引导用户检查 Token scope 或仓库权限设置 |
| 403（其他） | 禁止访问 | 检查 body 中的 `message` 字段，根据具体原因引导用户（如 "Repository access blocked" → 检查 IP 允许列表） |
| 404 | Not Found | 验证 owner/repo/资源 ID 是否正确；检查仓库是否为 private（可能需要额外 scope）；提示用户确认资源是否存在 |
| 409 | Conflict | 存在并发修改冲突（如 merge conflict），报告具体冲突原因，由用户决定处理方式 |
| 422 | Validation Failed | 检查请求参数格式（如缺少必填字段、SHA 不匹配、branch 已存在等），解析 `errors` 数组获取详细原因，修正后重试 |
| 429 | Rate Limited | 执行限流处理算法（见 §8.3）；**所有 HTTP 方法均可重试** |
| 500 | Internal Server Error | 仅对幂等方法（GET/DELETE）自动重试（最多 2 次，指数退避）；POST/PATCH/PUT 报告错误，由用户决定是否重试 |
| 502 | Bad Gateway | 同 500 处理策略 |
| 503 | Service Unavailable | 同 500 处理策略 |

**403 三义歧义处理（关键）**：收到 403 时，AI **必须**先检查响应 body：
1. 包含 `"secondary rate limit"` → **等待重试**（不是权限问题）
2. 包含 `"Resource not accessible"` → **权限不足**（停止，引导用户）
3. 其他 → **读取 message 字段**判断具体原因

### 8.2 Link 头分页契约（算法）

GitHub REST API 使用 `Link` Header 进行分页（不同于 Notion 的 `has_more` / `next_cursor` 模式）。

```
FUNCTION paginate(endpoint, params):
  all_results = []
  url = endpoint + "?" + urlencode(params) + "&per_page=100"

  LOOP:
    response = CALL GET url
    all_results.APPEND(response.body)

    link_header = response.headers["Link"]
    IF link_header CONTAINS rel="next" THEN
      url = EXTRACT url FROM link_header WHERE rel="next"
      GOTO LOOP
    ELSE
      RETURN all_results
    END IF
```

**Link Header 解析规则（强制）**：

1. **始终使用 `per_page=100`**（GitHub 默认仅 30 条，会导致静默数据截断）
2. **解析 `Link` Header**：格式为 `<URL>; rel="next", <URL>; rel="last"`，提取 `rel="next"` 对应的 URL
3. **禁止将部分结果当作完整结果呈现给用户** — 若存在 `rel="next"`，必须继续翻页或明确告知用户"还有更多数据"
4. 翻页完成后，告知用户"已获取全部 N 条结果"
5. **bash 解析示例**：
   ```bash
   # 从 Link Header 中提取 next URL
   next_url=$(echo "$link_header" | grep -oP '<\K[^>]+(?=>; rel="next")')
   ```

### 8.3 双路限流处理算法

GitHub 有两层限流机制：

**Primary Rate Limit（主限流）**：
- 认证用户：5,000 requests/hour
- 通过 `x-ratelimit-remaining` 和 `x-ratelimit-reset` Header 监控
- 触发时返回 HTTP 429

**Secondary Rate Limit（次级限流）**：
- 针对短时间内大量请求的额外保护
- 触发时返回 HTTP 403（body 含 `"secondary rate limit"`）
- 通常由并发请求或短时间内创建大量内容触发

```
FUNCTION handle_rate_limit(response, attempt):
  IF attempt > MAX_RETRIES(2) THEN
    FAIL "超过最大重试次数，请稍后再试"
  END IF

  # 检查是否为 429（主限流）
  IF response.status == 429 THEN
    IF response.headers["retry-after"] EXISTS THEN
      wait_seconds = response.headers["retry-after"]
    ELIF response.headers["x-ratelimit-reset"] EXISTS THEN
      wait_seconds = response.headers["x-ratelimit-reset"] - NOW_UNIX
    ELSE
      wait_seconds = MIN(1 * 2^attempt + random(0, 1), 60)
    END IF
  END IF

  # 检查是否为 403 次级限流
  IF response.status == 403 AND response.body CONTAINS "secondary rate limit" THEN
    IF response.headers["retry-after"] EXISTS THEN
      wait_seconds = response.headers["retry-after"]
    ELSE
      wait_seconds = MIN(60 * 2^attempt, 300)  # 次级限流等待更久
    END IF
  END IF

  SLEEP(MIN(wait_seconds, 300))
  RETRY request
```

**x-ratelimit-* Header 说明**：

| Header | 说明 | 示例 |
|--------|------|------|
| `x-ratelimit-limit` | 每小时总配额 | `5000` |
| `x-ratelimit-remaining` | 当前窗口剩余配额 | `4999` |
| `x-ratelimit-reset` | 配额重置时间（Unix 时间戳） | `1713456000` |
| `x-ratelimit-used` | 当前窗口已使用配额 | `1` |
| `x-ratelimit-resource` | 限流资源类型 | `core` / `search` / `graphql` |

**主动预防**：
- 每次请求后检查 `x-ratelimit-remaining`，若低于 100 则降低请求频率
- 若为 0，等待至 `x-ratelimit-reset` 时间点后再请求

### 8.4 通用约定

1. **Base URL**：`https://api.github.com`（所有端点都基于此地址）
2. **API 版本**：所有请求必须附带 `X-GitHub-Api-Version: 2022-11-28` Header
3. **Accept Header**：所有请求建议附带 `Accept: application/vnd.github+json`
4. **Content-Type**：POST/PATCH/PUT 请求体为 JSON（`application/json`）；文件上传为 `application/octet-stream` 或 `multipart/form-data`
5. **Token 传递**：仅通过 `Authorization: Bearer <token>` Header 传递
6. **ID 格式**：GitHub 使用整数 ID（如 `123456789`），不同于 UUID 格式
7. **日期格式**：ISO 8601（`YYYY-MM-DDTHH:MM:SSZ`）
8. **空响应**：DELETE 和某些 PUT 操作成功返回 HTTP 204（无 body）
9. **PowerShell 注意**：`irm` 是 `Invoke-RestMethod` 别名；文件上传需用 `curl.exe`；续行符为反引号 `` ` `` 而非 `\`

### 8.5 Search API 独立限流说明

Search API 有独立的限流配额，不与核心 API 共享：

| 限制 | 值 | 说明 |
|------|-----|------|
| 认证用户 | 30 requests/min | 通过 `x-ratelimit-resource: search` 识别 |
| 未认证 | 10 requests/min | 不适用（本 SKILL 始终使用 Token） |

**Search 限流处理**：
- Search 限流通过 `x-ratelimit-resource: search` 区分
- 触发 429 后按 §8.3 算法处理，但等待时间通常以分钟为单位
- **建议**：批量搜索时在每次请求间间隔 2-3 秒，主动避免触发限流
- Search 结果最多返回前 1,000 条匹配项（GitHub 硬限制），超出需用更精确的查询条件缩小范围
