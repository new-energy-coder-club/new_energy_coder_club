MICA关键性验证项目文档
======================

欢迎来到 **MICA关键性验证项目** 的官方文档！

本项目致力于验证MICA混合关键部署框架在openEuler Embedded中的集成，
为混合关键系统提供高效、可靠的部署解决方案。

.. note::
   本项目正在积极开发中，预期2025年底完成。
   文档会随着项目进展持续更新。

快速导航
--------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🚀 快速开始
      :link: getting_started/index
      :link-type: doc

      新手入门指南，30分钟快速上手

   .. grid-item-card:: 📖 用户指南
      :link: user_guide/index
      :link-type: doc

      详细的使用说明和配置指南

   .. grid-item-card:: 🔧 开发者指南
      :link: developer_guide/index
      :link-type: doc

      API参考和开发贡献指南

   .. grid-item-card:: 💡 示例代码
      :link: examples/index
      :link-type: doc

      实用的代码示例和最佳实践

项目特性
--------

✨ **混合关键部署**
   在单一硬件平台上同时运行不同安全等级的应用程序

⚡ **实时性保证**
   支持RT-Thread等RTOS，满足严格的实时性要求

🔧 **高度集成**
   与openEuler Embedded深度集成，提供统一的开发体验

📊 **性能优化**
   优化资源利用效率，降低硬件成本

技术架构
--------

.. mermaid::

   graph TB
       A[openEuler Embedded] --> B[MICA Framework]
       B --> C[RT-Thread RTOS]
       C --> D[Hardware Platform]
       
       A --> E[Linux Applications]
       B --> F[Mixed-Critical Manager]
       C --> G[Real-time Applications]
       D --> H[ARM Cortex-A/M Series]

应用场景
--------

🏭 **工业控制**
   实时控制系统与数据处理系统的混合部署

🚗 **汽车电子**
   安全关键系统与信息娱乐系统的协同运行

🤖 **机器人系统**
   运动控制与智能决策的统一平台

🌐 **物联网设备**
   设备控制与云端通信的集成方案

目录结构
--------

.. toctree::
   :maxdepth: 2
   :caption: 文档内容:

   getting_started/index
   user_guide/index
   developer_guide/index
   examples/index

.. toctree::
   :maxdepth: 1
   :caption: 项目信息:

   changelog
   license
   contact

索引和搜索
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

---

.. note::
   Built with `Sphinx <https://www.sphinx-doc.org/>`_ using a theme provided by `Read the Docs <https://readthedocs.org/>`_.
   
   项目源码托管在 `Gitee <https://gitee.com/new_energy_coder_club/mica-validation>`_，欢迎提交改进建议。