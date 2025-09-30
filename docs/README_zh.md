# autohack-next

> [English](../README.md) | 简体中文

一个高度自定义的竞技性编程 Hack 工具，使用 Python 编写。

[autohack](https://github.com/gi-b716/autohack) 完全重构的版本，拥有更清晰的配置，经过重新设计的界面，和更强劲的性能。

## 安装

autohack-next 作为包发布在了 PyPI 上，使用 Python 包管理器安装即可，亦可以下载构建好的二进制文件运行。autohack-next 的 dev 版本发布在了 TestPyPI 上。

## 使用

运行如下命令：

```bash
python -m autohack
```

或

```bash
autohack
```

第一次运行时，会在当前目录生成 `.autohack` 文件夹并退出。

在 `.autohack/config.json` 中调整设置后再次运行即可。

## 构建

参见 [release.yml](../.github/workflows/release.yml)

## Checker 自定义

可以在 `checker.name` 配置项中使用自定义的 checker。

`autohack-next` 会从 `.autohack/checkers` 文件夹中读取名为 `{checker.name}.py` 的文件。

自定义 checker 文件需要一个 activate 函数，接收参数列表即 `checker.args` 配置项，返回 checker 函数。

checker 函数需要接受输入、输出、答案及参数列表，返回一个元组。元组包含一个布尔值，Accepted 时为真，另外包含一个字符串即 checker 输出。

可选地，自定义 checker 可以包含一个 deactivate 函数，其接收参数列表，返回 None，可以起到后处理的用处。

形式化地说，您的函数签名应该如下。

```python
# src/autohack/core/checker.py

from typing import Callable, TypeAlias

checkerType: TypeAlias = Callable[[bytes, bytes, bytes, dict], tuple[bool, str]]
activateType: TypeAlias = Callable[[dict], checkerType]
deactivateType: TypeAlias = Callable[[dict], None]
```

特殊地，有几个内置 checker。

### builtin_basic

全文比较输出与答案，忽略行末空格与文末换行。

#### 参数

无。

### builtin_always_ac

测试用，永远返回 Accepted.

#### 参数

无。

### builtin_testlib

对 [testlib](https://github.com/MikeMirzayanov/testlib/) 的支持。

#### 参数

##### compiler

编译 checker 使用的编译器路径。

默认：`g++`

##### checker

checker 文件名。

默认：`checker.cpp`

##### compile_args

编译参数。

默认：`[]`
