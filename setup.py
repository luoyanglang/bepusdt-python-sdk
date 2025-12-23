"""BEpusdt Python SDK 安装配置"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bepusdt",
    version="0.2.1",
    author="luoyanglang",
    author_email="luoyanglang@users.noreply.github.com",
    description="BEpusdt 支付网关 Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luoyanglang/bepusdt-python-sdk",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    keywords="bepusdt payment usdt trx cryptocurrency",
    project_urls={
        "Bug Reports": "https://github.com/luoyanglang/bepusdt-python-sdk/issues",
        "Source": "https://github.com/luoyanglang/bepusdt-python-sdk",
        "Documentation": "https://github.com/luoyanglang/bepusdt-python-sdk#readme",
    },
)
