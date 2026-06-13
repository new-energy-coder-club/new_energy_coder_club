# FBS-BookWriter · OpenClaw（v2.1.2）

本仓库即 **OpenClaw** 通道技能**源码树**（与主项目 `npm run pack:openclaw` 产出一致），仓库根目录即为技能根：`SKILL.md`、`package.json`、`references/`、`scripts/` 等。不含 WorkBuddy / CodeBuddy 市场清单。

## ClawHub

- 列表页：<https://clawhub.ai/skills/fbs-bookwriter>（发布后可用）
- 安装：`openclaw skills install fbs-bookwriter` 或 `npx clawhub@latest install fbs-bookwriter`，然后在技能根目录执行 `npm install`
- 维护者从主仓发布：`npm run publish:clawhub`（需先执行 `npx clawhub@latest login`）

## 使用方式（Git 克隆）

将仓库克隆为技能目录名 **`fbs_bookwriter`**（与 `SKILL.md` 中 `name` 一致），再安装依赖：

```bash
git clone https://github.com/duhongchao-Fbsir/fbs-bookwriter-openclaw.git fbs_bookwriter
cd fbs_bookwriter
npm install
```

然后按包内 [`SKILL.md`](./SKILL.md)「安装（OpenClaw）」配置 OpenClaw 技能扫描路径，并用 `openclaw skills list` 确认加载。

## 版本

当前：**2.1.2**。上游主页：<https://fbs-bookwriter.u3w.com/>
