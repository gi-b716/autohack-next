# autohack-next

> English | [简体中文](./docs/README_zh.md)

A highly customizable competitive programming Hack tool written in Python.

A completely refactored version of [autohack](https://github.com/gi-b716/autohack) with clearer configuration, a redesigned interface, and more powerful performance.

## Installation

autohack-next is published as a package on PyPI. Install it using a Python package manager, or you can download pre-built binary files to run.

## Usage

Run the following command:

```bash
python -m autohack
```

or

```bash
autohack
```

On the first run, it will generate a `.autohack` folder in the current directory and exit.

After adjusting the settings in `.autohack/config.json`, run it again to start using.

## Build

See [release.yml](./.github/workflows/release.yml)

## Custom Checker

You can use custom checkers in the `checker.name` configuration option.

`autohack-next` will read files named `{checker.name}.py` from the `.autohack/checkers` folder.

Custom checker files need an activate function that receives the argument list (i.e., the `checker.args` configuration option) and returns a checker function.

The checker function needs to accept input, output, answer, and argument list, and return a tuple. The tuple contains a boolean value (true when Accepted) and a string (the checker output).

Formally, your function signatures should be as follows:

```python
from typing import Callable, TypeAlias

checkerType: TypeAlias = Callable[[bytes, bytes, bytes, dict], tuple[bool, str]]
activateType: TypeAlias = Callable[[dict], checkerType]
```

There are several built-in checkers available.

### builtin_basic

Compares output with answer text-wise, ignoring trailing spaces at line ends and final newlines.

#### Arguments for builtin_basic

None.

### builtin_always_ac

For testing purposes, always returns Accepted.

#### Arguments for builtin_always_ac

None.

### builtin_testlib

Support for [testlib](https://github.com/MikeMirzayanov/testlib/).

#### Arguments for builtin_testlib

##### compiler

Compiler path used to compile the checker.

Default: `g++`

##### checker

Checker filename.

Default: `checker.cpp`

##### compile_args

Compilation arguments.

Default: `[]`
