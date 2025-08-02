"""
Internationalization support for autohack.
"""

import locale
import os
from pathlib import Path

# Get the package directory
PACKAGE_DIR = Path(__file__).parent
LOCALE_DIR = PACKAGE_DIR / "locale"

# Simple translation dictionaries
TRANSLATIONS = {
    "zh_CN": {
        'Data folder path: "{0}"': '数据文件夹路径："{0}"',
        "Client ID: {0}": "客户端ID：{0}",
        "Initialized.": "已初始化。",
        "Compile {0}.": "编译{0}。",
        "Compile finished.": "编译完成。",
        "{0} compilation failed: {1}": "{0}编译失败：{1}",
        "{0} compiled successfully.": "{0}编译成功。",
        "{0}: Generate input.": "{0}：生成输入。",
        "{0}: Generate answer.": "{0}：生成答案。",
        "{0}: Run source code.": "{0}：运行源代码。",
        "{0}: Accepted.": "{0}：通过。",
        "Generating data {0}.": "正在生成数据{0}。",
        "Generating answer for data {0}.": "正在为数据{0}生成答案。",
        "Run source code for data {0}.": "为数据{0}运行源代码。",
        "Input generation failed: {0}": "输入生成失败：{0}",
        "Answer generation failed: {0}": "答案生成失败：{0}",
        "Memory limit exceeded for data {0}.": "数据{0}内存超限。",
        "Time limit exceeded for data {0}.": "数据{0}时间超限。",
        "Runtime error for data {0} with return code {1}.": "数据{0}运行时错误，返回码{1}。",
        "Wrong answer for data {0}. Checker output: {1}": "数据{0}答案错误。检查器输出：{1}",
        "Finished. {0} data generated, {1} error data found.": "完成。生成了{0}个数据，发现{1}个错误数据。",
        "Memory limit exceeded for data {0}. Hack data saved to {1}.": "数据{0}内存超限。破解数据已保存到{1}。",
        "Time limit exceeded for data {0}. Hack data saved to {1}.": "数据{0}时间超限。破解数据已保存到{1}。",
        "Runtime error for data {0} with return code {1}. Hack data saved to {2}.": "数据{0}运行时错误，返回码{1}。破解数据已保存到{2}。",
        "Wrong answer for data {0}. Hack data saved to {1}. Checker output: {2}": "数据{0}答案错误。破解数据已保存到{1}。检查器输出：{2}",
        'Config file path: "{0}"': '配置文件路径："{0}"',
        "Config file created.": "配置文件已创建。",
        "Config file updated.": "配置文件已更新。",
        "Config file loaded.": "配置文件已加载。",
        'Get config entry: "{0}" = "{1}"': '获取配置项："{0}" = "{1}"',
        'Modify entry: "{0}" = "{1}"': '修改配置项："{0}" = "{1}"',
        'Log file: "{0}"': '日志文件："{0}"',
        "Log level: {0}": "日志级别：{0}",
        "Logger initialized.": "日志记录器已初始化。",
        "No differences found.": "未发现差异。",
        "Difference found at line {0}, column {1}.": "在第{0}行第{1}列发现差异。",
    },
    "en_US": {},  # English is the default, no translation needed
}

# Current language
_current_language = None


def setup_i18n(language=None):
    """
    Setup internationalization.

    Args:
        language: Language code (e.g., 'zh_CN', 'en_US'). If None, auto-detect.
    """
    global _current_language

    if language is None:
        # Auto-detect system language
        try:
            detected = locale.getdefaultlocale()[0]
            language = detected if detected else "en_US"
        except (TypeError, ValueError):
            language = "en_US"

    _current_language = language


def _(message):
    """
    Translate a message.

    Args:
        message: The message to translate

    Returns:
        The translated message
    """
    if _current_language is None:
        setup_i18n()

    if _current_language in TRANSLATIONS:
        return TRANSLATIONS[_current_language].get(message, message)
    return message


def ngettext(singular, plural, n):
    """
    Get the correct plural form for a number.

    Args:
        singular: Singular form
        plural: Plural form
        n: The number

    Returns:
        The correct plural form
    """
    # For Chinese, there's no plural distinction
    if _current_language and _current_language.startswith("zh"):
        return _(singular)

    # For English and other languages
    translated_singular = _(singular)
    translated_plural = _(plural)
    return translated_singular if n == 1 else translated_plural


# Initialize on import
setup_i18n()
