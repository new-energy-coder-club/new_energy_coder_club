# RISC-V × AI 方向 OSPP 转型优化方案

> 状态：草案 v1（2026-09-17）
> 目标：以 2027 开源之夏（OSPP）为锚点，把社区从"竞赛资料库"升级为"RISC-V × 边缘 AI 开源项目社区"
> 负责人：待认领（建议 @DarrenPig 牵头，Maintainers 周会评审）

---

## 1. 现状评估（为什么说"基础已有，叙事缺失"）

### 1.1 已有的 RISC-V 资产（但未以 RISC-V 叙事组织）

| 资产 | 位置 | 状态 |
|---|---|---|
| 嘉楠 K230（RISC-V 双核 C908 + KPU NPU）轮腿机器狗，含可部署的 kmodel 图像分类代码（nncase 2.9.0） | `projects/robotics/机器狗-k230/code/K230_KFS_detection/` | ✅ 真代码 + 模型，仓库内最有价值的 RISC-V+AI 资产 |
| 海思 WS63/WS63E 星闪（NearLink）SoC（RISC-V 内核），SLE 遥控手柄，联动 openEuler Embedded | `projects/星闪手柄/` | ✅ 有样例代码与 OSPP 2024 参与记录 |
| K230 / 树莓派 5 / Jetson Nano 并列为视觉计算平台规划 | `competitions/CURC2026ROBOCON/视觉SIG/` | 📋 规划中 |

### 1.2 已有的 AI 资产

- K230 kmodel 端侧推理（唯一已落地部署的边缘 AI）
- 树莓派 5 + PyTorch 预测性维护（`projects/5axis-fluid-workstation/`，源码在外部仓库）
- YOLO/TensorRT/OpenCV 学习计划（CURC2026 视觉 SIG）
- `projects/templates/ai_project_template/` 标准 AI 项目骨架

### 1.3 已有的 OSPP 渠道（已验证可走通）

- `projects/research-horizontal/AGL-openEuler.md`：AGL × openEuler Embedded OSPP 结项报告（完整评审流程经验）
- `projects/星闪手柄/`："基于 openEuler Embedded 的星闪开源应用案例开发"（OSPP 2024）
- 2025-06 已完成一项开源之夏结项（`competitions/2025-robocon/Readme.md`）

### 1.4 关键短板（按优先级）

1. **无 RISC-V 叙事**：全仓库搜索 "RISC-V" 零命中，硬件在用但品牌未建立
2. **无 OSPP 专区**：没有课题申报模板、导师页、学生指南、历届归档
3. **无 CI/自动化**：`.github/workflows/` 不存在
4. **许可证声明矛盾**：README 徽章写 MIT，`LICENSE.md` 实为木兰 PSL v2
5. **工程卫生**：PDF/ZIP/APK/kmodel 等大文件未走 Git LFS；README 多处 404 链接；`docs/resources.md` 引用不存在的 `build/competition_index.md`；`.gitmodules` 中 `2027CURC-ROBOCON` 子模块 URL 指向仓库自身
6. **ROADMAP 无技术路线**：`docs/ROADMAP.md` 仅 5 行，无 RISC-V/AI 方向

---

## 2. 转型定位

**一句话定位**：面向 RISC-V 端侧 AI（KPU/NPU 推理 × 机器人 × 星闪互联）的开源实践社区，依托 openEuler Embedded / RT-Thread 生态，承接开源之夏课题。

**为什么选这个定位**：
- K230 是国产 RISC-V AI SoC 里生态最活跃的方向之一（嘉楠开发者社区、nncase 工具链开源）
- OSPP 中 RISC-V（PLCT/甲辰计划）、openEuler、RT-Thread 社区每年都有大量端侧 AI 课题，社区已有合作记录
- 与现有竞赛（ROBOCON 视觉、机器狗）形成"竞赛喂课题、课题反哺竞赛"的闭环

---

## 3. 分阶段实施计划

### 阶段 0：工程卫生修复（2 周，good first issue 池）

| # | 任务 | 产出 |
|---|---|---|
| 0.1 | 统一许可证：确认以 Mulan PSL v2 为准，修正 README 徽章与说明 | README/徽章修复 PR |
| 0.2 | 修复死链：`projects/robotics/mechdog-k230-kfs/` → `机器狗-k230/`；补 `docs/indexes/competition_index.md` 或改引用 | 链接检查通过 |
| 0.3 | 修复 `.gitmodules`：移除或改正 `2027CURC-ROBOCON` 自引用 | 子模块配置正常 |
| 0.4 | Git LFS 扩容：`.gitattributes` 增加 `*.pdf *.zip *.apk *.exe *.kmodel *.STEP *.docx *.vsdx`（注意：已在库文件需 `git lfs migrate`，单独评审） | 仓库体积可控 |
| 0.5 | 引入 CI：markdown-lint + 死链检查（GitHub Actions / Gitee Go） | `.github/workflows/ci.yml` |

> 以上 5 项全部标记为 `good first issue`，既是修复又是新人入口。

### 阶段 1：RISC-V × AI 叙事建设（1 个月）

1. **README 重构**：项目快览表增加"技术栈"列（RISC-V K230 / KPU / nncase / 星闪 WS63 / openEuler Embedded），新增 RISC-V × AI 方向小节
2. **更新 `docs/ROADMAP.md`**：加入技术路线（本方案第 4 节课题池）与 OSPP 时间线
3. **新建 RISC-V SIG 目录**：`projects/riscv-ai-sig/`（或直接复用 `projects/robotics/` 下建子目录），存放：
   - K230 开发环境搭建指南（nncase 2.9.0 工具链、kmodel 部署）
   - WS63 星闪开发指南
   - RISC-V 学习资源索引（PLCT 课程、香山文档等）
4. **英文 README**（`README_EN.md`）：OSPP 国际社区与 GitHub 曝光需要

### 阶段 2：OSPP 专区建设（1 个月，对接 2027 申报）

新建 `docs/ospp/` 目录结构：

```
docs/ospp/
├── README.md                  # OSPP 专区首页：什么是 OSPP、本社区参与方式
├── topics/                    # 课题池（每课题一个 md）
│   ├── TEMPLATE.md            # 课题申报模板：名称/难度/导师/技能要求/产出/参考
│   └── 2027/                  # 2027 年课题
├── mentors.md                 # 导师列表：姓名/方向/联系方式/可带人数
├── student-guide.md           # 学生指南：报名流程/申请书模板/时间线
└── archive/                   # 历届结项归档（迁移 AGL-openEuler.md、星闪 OSPP 记录）
```

**2027 OSPP 关键时间线**（往年节奏，以官网为准）：
- 2027-02 ~ 03：社区/导师报名，课题提交 → **2026-12 前完成课题池**
- 2027-04 ~ 05：学生报名与申请书提交
- 2027-06 ~ 09：开发期（中期考核）
- 2027-10 ~ 11：结项评审

**双渠道申报策略**：
- 渠道 A（已验证）：继续通过 openEuler / RT-Thread / 甲辰计划等成熟社区挂靠申报（AGL、星闪模式）
- 渠道 B（目标）：NEC 社区自身通过 OSPP 社区审核，独立发布课题（要求：有组织治理文档 ✅、导师 ✅、课题池 → 本方案补齐）

### 阶段 3：课题池建设（持续，首批 6 个课题建议）

| # | 课题 | 难度 | 依托资产 | 产出 |
|---|---|---|---|---|
| 1 | K230 KPU 端侧 YOLO 检测部署管线开源化（图像分类 → 目标检测） | 进阶 | `机器狗-k230/code/K230_KFS_detection/` | 可复现的训练→量化→部署全链路 + 文档 |
| 2 | K230 轮腿机器狗视觉栈重构：分类/检测/跟踪模块化，接 ROS 2 | 进阶 | `机器狗-k230/` | 开源视觉中间件包 |
| 3 | 基于 WS63 的星闪（NearLink）传感器组网 Demo × openEuler Embedded | 基础 | `星闪手柄/` | 可烧录固件 + 教程 |
| 4 | RISC-V 端侧 TinyML 推理基准：K230 vs ESP32-S3 vs 树莓派 5 横向评测 | 基础 | 现有三块硬件 | 开源 benchmark 报告 + 脚本 |
| 5 | AI 项目模板完善：补全 `ai_project_template` 空壳 src，加 CI 与单测样例 | 基础 | `projects/templates/ai_project_template/` | 可直接 fork 的模板 |
| 6 | nncase 模型 zoo 中文文档与 K230 部署案例翻译/增补（贡献上游） | 基础 | 嘉楠 nncase 上游 | 合入上游的 PR/MR（满足 OSPP 结项要求） |

> 课题设计原则：① 必须有仓库内可验证的起点资产；② 产出必须能合入上游或本仓库（OSPP 评审硬要求）；③ 难度梯度覆盖"基础/进阶"，匹配本专科生→研究生。

---

## 4. 验收指标（2027 OSPP 周期）

- [ ] 工程卫生：CI 绿灯、许可证一致、死链清零、大文件全走 LFS
- [ ] `docs/ospp/` 专区上线，含 ≥6 个申报就绪课题、≥3 名导师
- [ ] RISC-V 关键词进入 README 与 ROADMAP，K230/WS63 指南可复现
- [ ] 2027 OSPP：提交 ≥4 个课题，录取 ≥2 名学生，结项 ≥1 项
- [ ] 至少 1 个产出合入上游社区（nncase / openEuler / RT-Thread）

---

## 5. 风险与对策

| 风险 | 对策 |
|---|---|
| 导师精力不足（目前仅 3 名维护者） | 优先渠道 A 挂靠成熟社区；课题 1/4/5 可由高年级学生任副导师 |
| K230 硬件数量限制学生参与 | 课题 4/6 支持模拟器与纯软件产出；优先提供远程 SSH 到实验室开发板 |
| 仓库"资料库 > 代码库"形象影响 OSPP 审核 | 阶段 0/1 优先把 K230 代码整理为独立可构建工程，README 突出代码入口 |
| 大文件 LFS 迁移改写历史 | 单独评审，安排在 OSPP 申报空窗期（2026-11 前）执行 |
