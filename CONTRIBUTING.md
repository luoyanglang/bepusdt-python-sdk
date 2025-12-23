# 贡献指南

感谢你考虑为 BEpusdt Python SDK 做出贡献！

## 开发环境设置

1. Fork 并克隆仓库：
```bash
git clone https://github.com/yourusername/bepusdt-python-sdk.git
cd bepusdt-python-sdk
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

## 开发流程

1. 创建新分支：
```bash
git checkout -b feature/your-feature-name
```

2. 进行修改并确保代码质量：
```bash
# 代码格式化
black bepusdt tests

# 类型检查
mypy bepusdt

# 代码检查
flake8 bepusdt

# 运行测试
pytest
```

3. 提交更改：
```bash
git add .
git commit -m "feat: 添加新功能"
```

4. 推送并创建 Pull Request：
```bash
git push origin feature/your-feature-name
```

## 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 代码规范

- 遵循 PEP 8 规范
- 使用类型提示
- 编写清晰的文档字符串
- 保持代码简洁易读

## 测试

- 为新功能添加测试
- 确保所有测试通过
- 保持测试覆盖率

## 问题反馈

如果发现 bug 或有功能建议，请创建 Issue 并提供：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、操作系统等）

感谢你的贡献！
