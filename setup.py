"""PEP 517 构建兼容入口。

项目元数据主要由 pyproject.toml 管理，版本由 setuptools_scm 从 Git tag 推导。
"""

from setuptools import setup

setup(license="MIT", license_files=["LICENSE"])
