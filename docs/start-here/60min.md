# 新人 60 分钟上手：跑通 NEC 最小 Demo + 提交第一个 PR

## 入门飞书文档： https://scn0bdoc8zxg.feishu.cn/wiki/QAtNwr244ir8ZekITEZcwpOZnkg

> 目标：**1 小时内**完成三件事：
> 1) 在本地跑通一个“无硬件也能跑”的 NEC 最小 Demo  
> 2) 提交一个很小但规范的 PR（文档也算贡献）  
> 3) 学会如何领取 `good first issue`，开始参与真实项目/竞赛任务

---

## 你将获得什么

- ✅ 能跑起来：`python docs/nec-quickstart/hello_nec.py`  
- ✅ 会产出：生成 `docs/nec-quickstart/out/run_log.csv`（仿真轨迹日志）
- ✅ 能贡献：完成一次标准 Git 提交 & PR
- ✅ 下一步明确：从 `good first issue` 开始做真实任务

---

## 前置条件（尽量少）

你需要：
- Git（能 `git --version`）
- Python 3.8+（能 `python --version`）
- 一个 Gitee 或 GitHub 账号（用于提 PR）

> 如果你是 Windows 用户：**推荐先用本地 Python + Git**，不要一上来就折腾虚拟机/WSL。
> 真要走 Linux 路线，等你做完这个 PR 再升级也不迟。

---

## 0-10 分钟：克隆仓库 & 进入目录

```bash
git clone https://gitee.com/darrenpig/new_energy_coder_club.git
cd new_energy_coder_club
```

检查版本：

```bash
git --version
python --version
```

---

## 10-25 分钟：跑通最小 Demo（无硬件）

直接运行：

```bash
python docs/nec-quickstart/hello_nec.py --seconds 20
```

你应该看到：

* 控制台输出：运行摘要 + 一个 ASCII 轨迹图
* 生成文件：`docs/nec-quickstart/out/run_log.csv`

> 如果你没看到 `out/run_log.csv`，先看本文末尾《常见问题》。

---

## 25-35 分钟：创建分支（为你的第一个 PR 做准备）

建议分支命名（任选其一）：

* `gfi/first-pr-<你的名字或ID>`
* `docs/first-pr-<你的名字或ID>`

```bash
git checkout -b gfi/first-pr-yourname
```

---

## 35-50 分钟：做一个“必过审”的小贡献（推荐：把自己写进新人墙）

打开文件：

* `docs/start-here/newcomers.md`

在末尾追加一行（示例）：

* `@your_id`｜方向：软件/硬件/机械/运营｜目标：完成第一个 good first issue｜设备：Windows / Mac / Linux｜时间：2025-12-24

> 你也可以顺手做一个小改进：修正文档里的拼写，比如 Linux / Founder / EDA 等。

---

## 50-60 分钟：提交 Commit + 发起 PR

### 1) git status 检查

```bash
git status
```

### 2) 提交（建议用 Conventional Commits 风格）

```bash
git add docs/start-here/newcomers.md
git commit -m "docs: add newcomer @your_id"
```

### 3) 推送到远端

```bash
git push -u origin gfi/first-pr-yourname
```

### 4) 在 Gitee/GitHub 上创建 PR

PR 标题建议：

* `docs: add newcomer @your_id`
  或
* `docs(start-here): add newcomer @your_id`

PR 描述里写清楚：

* 我跑通了 `docs/nec-quickstart/hello_nec.py`
* 我新增了新人墙记录
* 我想继续认领一个 `good first issue`

---

## 完成后下一步（强烈建议）

* 去 Issues 里筛选：`good first issue`
* 或直接看：《First Good Issue 小白看这里》
  * `docs/start-here/first-good-issue.md`

---

## 可选加速路线（做完 PR 再做）

### A) 有亚博智能套件的新同学（推荐入门）

* 推荐项目：MicroROS(ESP32)Robot
  `https://www.yahboom.com/study/MicroROS-ESP32` 
  资料下载密码：`ypom`

你将学到：

* VMware/虚拟机（或 WSL）
* ESP32/硬件基础
* ROS2 topic 发布订阅
* Linux + Docker 基础
* 雷达 SLAM 入门（看项目文档）

### B) 有一点基础（学过 C / 51 / 单片机）

* Yu_XBai 平衡小车（百度盘你们已有）
* MechDog 机器狗（百度盘你们已有）

---

## 常见问题（Troubleshooting）

### 1) `python: command not found`

* Windows：安装 Python 3（勾选“Add python to PATH”）
* macOS：可以用 `python3` 代替 `python`

```bash
python3 docs/nec-quickstart/hello_nec.py --seconds 20
```

### 2) 运行了但没有生成 `out/run_log.csv`

* 确认你在仓库根目录
* 确认路径存在：`docs/nec-quickstart/`
* 再运行一次：

```bash
python docs/nec-quickstart/hello_nec.py --seconds 5 --out docs/nec-quickstart/out
```

### 3) 我不知道下一步做什么

直接去：

* `docs/start-here/first-good-issue.md`
  从 **文档类 `good first issue`** 开始最稳。

