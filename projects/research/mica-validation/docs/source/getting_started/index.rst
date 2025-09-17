快速上手指南
============

欢迎使用MICA关键性验证项目！本指南将帮助您在30分钟内快速上手。

.. note::
   在开始之前，请确保您的系统满足基本要求：
   
   - Ubuntu 20.04 LTS 或更高版本
   - 至少 8GB RAM 和 50GB 可用磁盘空间
   - 稳定的网络连接

学习路径
--------

.. tabs::

   .. tab:: 新手入门 (30分钟)

      1. :doc:`installation` - 安装开发环境
      2. :doc:`quickstart` - 运行第一个示例
      3. :doc:`basic_concepts` - 理解核心概念

   .. tab:: 进阶开发 (2小时)

      1. :doc:`../user_guide/architecture` - 系统架构详解
      2. :doc:`../user_guide/configuration` - 配置管理
      3. :doc:`../developer_guide/integration` - 集成开发

   .. tab:: 专家应用 (1天)

      1. :doc:`../developer_guide/performance` - 性能优化
      2. :doc:`../user_guide/troubleshooting` - 故障排除
      3. :doc:`../developer_guide/contributing` - 贡献代码

环境准备
--------

系统要求
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - 组件
     - 最低要求
     - 推荐配置
   * - 操作系统
     - Ubuntu 18.04 LTS
     - Ubuntu 22.04 LTS 或更高
   * - 内存
     - 4GB RAM
     - 8GB RAM 或更多
   * - 存储
     - 90GB 可用空间
     - 350GB SSD 存储
   * - 网络
     - 基本网络连接
     - 高速宽带连接

依赖工具安装
~~~~~~~~~~~~

.. code-block:: bash

   # 更新系统包
   sudo apt-get update
   sudo apt-get upgrade -y

   # 安装基础开发工具
   sudo apt-get install -y \
       git \
       build-essential \
       python3 \
       python3-pip \
       curl \
       wget \
       vim

   # 安装Yocto构建依赖
   sudo apt-get install -y \
       gawk \
       wget \
       git-core \
       diffstat \
       unzip \
       texinfo \
       gcc-multilib \
       build-essential \
       chrpath \
       socat \
       cpio \
       python3 \
       python3-pip \
       python3-pexpect \
       xz-utils \
       debianutils \
       iputils-ping \
       python3-git \
       python3-jinja2 \
       libegl1-mesa \
       libsdl1.2-dev \
       pylint3 \
       xterm

快速开始
--------

第一步：获取源码
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 克隆主项目
   git clone https://gitee.com/openeuler/yocto-meta-openeuler.git
   cd yocto-meta-openeuler

   # 克隆MICA支持层
   git clone https://gitee.com/new_energy_coder_club/meta-mica.git

第二步：初始化环境
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 初始化构建环境
   source oe-init-build-env build-mica

   # 添加MICA支持层
   bitbake-layers add-layer ../meta-mica

第三步：构建镜像
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 构建基础镜像
   bitbake openeuler-image-mica

   # 构建完成后，镜像位于：
   # tmp/deploy/images/qemuarm64/

第四步：运行测试
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 启动QEMU模拟器
   runqemu qemuarm64 openeuler-image-mica

   # 在QEMU中测试MICA功能
   mica-test --basic

验证安装
--------

运行以下命令验证安装是否成功：

.. code-block:: bash

   # 检查MICA版本
   mica --version

   # 运行基础测试
   mica-test --all

   # 查看系统状态
   mica status

预期输出：

.. code-block:: text

   MICA Framework v1.0.0
   ✓ openEuler Embedded: Ready
   ✓ RT-Thread Integration: Active
   ✓ Mixed-Critical Manager: Running
   ✓ Hardware Abstraction: OK

下一步
------

恭喜！您已经成功完成了MICA项目的基础安装。接下来您可以：

- 📖 阅读 :doc:`../user_guide/index` 了解详细使用方法
- 🔧 查看 :doc:`../developer_guide/index` 学习开发技巧
- 💡 浏览 :doc:`../examples/index` 获取实用示例
- 🐛 遇到问题时参考 :doc:`../user_guide/troubleshooting`

.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   quickstart
   basic_concepts