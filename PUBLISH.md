# 发布指南

## 发布到 PyPI

### 1. 准备工作

确保已安装发布工具：
```bash
pip install build twine
```

### 2. 更新版本号

在以下文件中更新版本号：
- `bepusdt/__init__.py`
- `setup.py`
- `CHANGELOG.md`

### 3. 运行测试

```bash
make test
make lint
```

### 4. 构建包

```bash
make build
```

这会在 `dist/` 目录生成：
- `bepusdt-x.x.x.tar.gz` (源码包)
- `bepusdt-x.x.x-py3-none-any.whl` (wheel 包)

### 5. 测试发布（可选）

先发布到 TestPyPI 测试：

```bash
# 注册 TestPyPI 账号: https://test.pypi.org/account/register/
make publish-test
```

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ bepusdt
```

### 6. 正式发布

```bash
# 注册 PyPI 账号: https://pypi.org/account/register/
make publish
```

### 7. 创建 Git 标签

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

### 8. 创建 GitHub Release

在 GitHub 上创建 Release，附上 CHANGELOG 内容。

## 版本号规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- `MAJOR.MINOR.PATCH`
- `1.0.0` - 主版本（不兼容的 API 修改）
- `0.1.0` - 次版本（向下兼容的功能性新增）
- `0.0.1` - 修订版本（向下兼容的问题修正）

## PyPI 配置

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token
```

## 发布检查清单

- [ ] 更新版本号
- [ ] 更新 CHANGELOG.md
- [ ] 运行所有测试
- [ ] 代码格式化和检查
- [ ] 更新 README.md（如有需要）
- [ ] 构建包
- [ ] 测试发布（TestPyPI）
- [ ] 正式发布（PyPI）
- [ ] 创建 Git 标签
- [ ] 创建 GitHub Release
- [ ] 更新文档网站（如有）

## 常见问题

### 上传失败

如果遇到 "File already exists" 错误，说明该版本已存在，需要：
1. 增加版本号
2. 重新构建
3. 重新上传

### 包名冲突

如果包名已被占用，需要修改 `setup.py` 中的 `name` 字段。

### API Token

推荐使用 API Token 而不是用户名密码：
1. 登录 PyPI
2. Account Settings → API tokens
3. 创建新 token
4. 配置到 `~/.pypirc`
