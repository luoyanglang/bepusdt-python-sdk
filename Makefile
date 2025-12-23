.PHONY: help install dev test lint format clean build publish

help:
	@echo "BEpusdt Python SDK - 开发命令"
	@echo ""
	@echo "make install    - 安装包"
	@echo "make dev        - 安装开发依赖"
	@echo "make test       - 运行测试"
	@echo "make lint       - 代码检查"
	@echo "make format     - 代码格式化"
	@echo "make clean      - 清理构建文件"
	@echo "make build      - 构建发布包"
	@echo "make publish    - 发布到 PyPI"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=bepusdt --cov-report=html --cov-report=term

lint:
	flake8 bepusdt tests
	mypy bepusdt

format:
	black bepusdt tests examples

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	python -m twine upload dist/*

publish-test: build
	python -m twine upload --repository testpypi dist/*
