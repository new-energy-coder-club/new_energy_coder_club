<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://gitee.com/darrenpig/new_energy_coder_club">
    <img src="https://gitee.com/darrenpig/new_energy_coder_club/raw/master/shared/images/Image/Logo.png" alt="Logo" width="120">
  </a>

  <h1 align="center">NEC 新能源开发者社区</h1>
  <p align="center"><strong>面向新能源 × 机器人竞赛与实战项目的开源工程社区</strong></p>
  <p align="center">
    <a href="https://www.newenergycoder.club"><strong>官网（Website）»</strong></a>
    &nbsp;|&nbsp;
    <a href="https://scn0bdoc8zxg.feishu.cn/wiki/QAtNwr244ir8ZekITEZcwpOZnkg"><strong>快速上手（Get Started）»</strong></a>
    &nbsp;|&nbsp;
    <a href="https://scn0bdoc8zxg.feishu.cn/wiki/S10LwzVZdiWLwxkEnEqcTcmEn6e"><strong>知识库（Docs）»</strong></a>
  </p>
</div>
> 260121提交指南：https://scn0bdoc8zxg.feishu.cn/docx/QkkYdBJE0o2Q9Xx9O5ocIoWZnde
---

# NEC · New Energy Coder Community

[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)[![Chat](https://img.shields.io/badge/Chat-QQ-blue?style=flat-square)](https://gitee.com/darrenpig/new_energy_coder_club/issues/IDATOS)[![Open Issues](https://img.shields.io/github/issues/darrenpig/new_energy_coder_club?label=open%20issues)](https://github.com/darrenpig/new_energy_coder_club/issues)[![Open PRs](https://img.shields.io/github/issues-pr/darrenpig/new_energy_coder_club?label=open%20PRs)](https://github.com/darrenpig/new_energy_coder_club/pulls)[![Docs](https://img.shields.io/badge/docs-%E2%9C%94%20complete-brightgreen)](docs/)
[![Version](https://img.shields.io/github/v/tag/darrenpig/new_energy_coder_club?label=Version)](https://github.com/darrenpig/new_energy_coder_club/releases)[![Project Status](https://img.shields.io/badge/Project%20Status-Active-green)](https://github.com/darrenpig/new_energy_coder_club)[![Website](https://img.shields.io/badge/Website-newenergycoder.club-orange?style=flat-square)](https://www.newenergycoder.club/)[![Knowledge Base](https://img.shields.io/badge/Knowledge%20Base-Feishu-blue?style=flat-square)](https://scn0bdoc8zxg.feishu.cn/wiki/S10LwzVZdiWLwxkEnEqcTcmEn6e)

## About NEC
NEC 是面向新能源与机器人竞赛的开源工程社区，提供模块化工程基线与赛季全周期资产，支持线上协作与 A416 线下实验室联动。

# 下面是常州工NEC战队的CURC-ROBOCON赛季仓库 


仓库由NEC托管负责 常州工学院 2026 年的赛季开源参赛记录

- 团队分为：机构、视觉、运营 三大技术方向
- 参与赛项：主赛 狗赛 排球

### 机构（mechanical）机械+电控

- CAD：装配体 + 关键零件（标版本号）
- BOM：采购清单（导出表 + 供应商链接）
- 加工图：PDF/DXF（能下发加工）
- 组装说明：步骤 + 扭矩 + 注意事项
- 标定/机构参数：如轮距、连杆长度等

### 视觉 SIG（Visual SIG）算法+硬件+场务

- **上位机/视觉算法**：识别、训练、推理优化、上位机界面
- **硬件调试与驱动/接口**：相机/摄像头、K230/树莓派、供电通信、驱动与接口稳定性，通信线缆的型号
- **场务支持与测试环境**：测试场搭建、标定流程、数据采集与复现环境

### 运营（operations）招商+宣传+合规

- 宣传物料：海报、推文、视频脚本
- 赞助招商：赞助方案、致谢墙、合作流程
- 赛务：报名材料、行程、物资清单、对接记录
- 影像归档：比赛日素材索引（统一命名）

------

## 目录结构
- [机构SIG](./机构SIG/)
  - [场务](./机构SIG/场务/) - 场地搭建、物资管理、现场保障
  - [机械](./机构SIG/机械/) - 机械设计、加工图纸、装配说明
  - [电控](./机构SIG/电控/) - 电路设计、嵌入式开发、联调支持
- [视觉SIG](./视觉SIG/) - 视觉算法、上位机开发、数据集管理
- [运营SIG](./运营SIG/) - 宣传物料、赞助招商、赛务统筹

## 命名与版本规范

**文件命名**

- 图片：`YYMMDD_主题_作者.jpg`
- 会议纪要：`YYMMDD_meeting_<event>.md`
- 机构版本：`assy_v0.3.step` / `assy_v0.3.f3d`
- 代码 Tag：`curc2026-r1`、`curc2026-r2`、` curc2026-dog `、、` curc2026-ball `



------

## 已有工作

- https://github.com/NEC-CuCu/coworkers_for_KFS
- https://gitee.com/hnuyuelurm/basic_framework 
- https://gitee.com/tarsgo-embedded/UIML 
- https://gitee.com/x-robot/XRobot/tree/dev/


## 推荐课程

| 课程名称 | 来源 | 适用对象 | 链接 |
| :--- | :--- | :--- | :--- |
| **中科大 RM 电控合集** | USTC | 电控 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **哈工大竞培营课程** | HIT | 通用/机械/视觉 | [B站视频](https://www.bilibili.com/video/BV1iH4jz4EPo) |
| **华科机械培训** | HUST | 机械 | [B站视频](https://www.bilibili.com/video/BV1DgnHzmEXK) |
| **工业相机 SDK 实操** | 海康机器人 | 视觉 | [B站视频](https://www.bilibili.com/video/BV1VnBTBiE7R) |
| **OpenCV+YOLO 目标检测** | - | 视觉 | [B站视频](https://www.bilibili.com/video/BV1M7oMYXE5h) |
| **树莓派5 视觉部署** | 亚博智能 | 视觉 | [B站视频](https://www.bilibili.com/video/BV1zCWYzvEA7) |
| **中科大 RM 运营课程** | USTC | 运营 | [B站视频](https://www.bilibili.com/video/BV1h4421F7sp) |

## 贡献者 (Contributors)

感谢以下CURC-ROBOCON26常州工学院参赛队正式成员的提交与贡献：

- **机构组**：庄皓钧、毕卫亭、张孟驰、白逸鸣、卢王淳、魏卫、王欣怡、孙诗睿、梁新雷、文钰婷、孟洁、岳添俊、李畅畅
- **视觉组**：卢永杰、郭童童、汪奕希、杨彩妮、白逸鸣
- **运营组**：韩祺冉、严文颖、张岩皓、徐海婷

## 每日工作：
- 260120 @Darrenpig 创建分支，学习UIML等代码。进行技术培训 @卢王淳  新建CURC26团队-常州工学院队 ， 开始哈工大竞培 学习 第1节
- 260122 @DarrenPig NEC内部会+培训 shell+Git，组织成员交流
- 260126 @卢王淳 组织机构组开会，进度及建议交流汇总； @卢永杰 组织视觉组例会，安排进度； @徐海婷 组织运营组例会，进行运营安排；最终与 @DarrenPig 进行交接。 