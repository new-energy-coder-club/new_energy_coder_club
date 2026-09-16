# NOTICE — 第三方代码与许可声明

本项目（轮腿机器狗 K230）包含或衍生自以下第三方组件。本仓库整体采用 [木兰宽松许可证第 2 版（Mulan PSL v2）](../../../LICENSE.md)，第三方组件按其各自许可证使用，版权归原作者/厂商所有。

## 第三方代码

| 组件 | 位置 | 来源 | 许可/说明 |
|---|---|---|---|
| K230 图像分类推理脚本 | `code/K230_KFS_detection/cls_image_1_3.py`、`cls_video_1_3.py` | 嘉楠科技（Canaan）官方部署示例改写，原作者署名 "Canaan Developer" | 嘉楠官方示例，随 CanMV/K230 SDK 发布 |
| kmodel 模型文件 | `code/K230_KFS_detection/*.kmodel` | 由 Canaan 在线训练平台训练生成（nncase 2.9.0 编译） | 本社区训练的模型产物；训练配置未开源（见 README「已知边界」） |
| ESP32 人脸/颜色识别工具代码 | `code/esp32_face_detection/`、`code/esp32_color_detection/` | 含乐鑫 esp-who 框架衍生代码（`who_ai_utils.cpp` 等） | esp-who 采用 [Apache-2.0](https://github.com/espressif/esp-who/blob/master/LICENSE) |
| MechDog 主控例程 | `code/mechdog_arm_main.py`、`code/ASR_Code.py` | 幻尔科技（Hiwonder）MechDog 官方例程改写 | 依赖幻尔闭源 Python 库，仅可在幻尔硬件上运行 |

## 外部资料链接

README 中的百度网盘链接为幻尔（Hiwonder）官方产品资料，版权归原作者所有，本仓仅作导航引用。

---

> 如发现出处标注遗漏，请提 Issue 或直接 PR 修正。
