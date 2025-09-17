# RT-Thread 构建支持

本元构建层(meta-layer)包含了在openEuler Yocto构建环境下集成构建RT-Thread的相关配置和配方。

## 使用

1. RT-Thread代码包的准备： 应事先将RT-Thread的[代码包](https://github.com/RT-Thread/rt-thread/archive/refs/tags/v4.0.5.tar.gz)下载放于OPENEULER_SP_DIR中，目录和文件名格式为rtthread/rtthread-${PV}.tar.gz.当前支持的最新版本是4.0.5

2. 在Yocto构建目录的bblayers.conf中添加相应的元构建层

```
  BBLAYERS ?= "/
  ......
  xxxxx/yocto-meta-openeuler/rtos/meta-openeuler-rtos /
  xxxxx/yocto-meta-openeuler/rtos/meta-rtthread /
  "
```

3. 构建rt-thread所需工具。构建rt-thread需要在构建主机上安装好scons构建工具，并在meta-openeuler-rtos/conf/layer.conf中填好构建RT-Thread所需工具链的路径和前缀。目前构建RT-Thread不能使用构建Linux的GCC工具链，例如xxx-linux-glibc-gcc，需要集成newlibc的工具链。一个例子如下所示：

```
OPENEULER_RTOS_TOOLCHAIN_DIR_aarch64 ?= "/opt/zephyr-sdk/aarch64-zephyr-elf/bin"
OPENEULER_RTOS_TOOLCHAIN_PREFIX_aarch64
```

4. 构建rt-thread.
```
    bitbake rtthread
```

rtthread构建的结果文件会安装在/lib/rtthread目录，并打包成rpm文件。