# 发布维护说明

本文记录 SDK 发布链路的当前约定和后续自动化维护方向。

## 当前发布流程

- 只有推送 `v*` 标签才会触发 PyPI 发布。
- 发布 workflow 会先运行格式检查、lint、测试、构建和包内容校验。
- `setuptools_scm` 根据 Git tag 推导包版本，tag 版本必须与 wheel
  metadata 中的版本一致。
- PyPI 发布成功后才创建 GitHub Release，并发送 Telegram 频道通知。
- Telegram 群组通知由频道自动转发，workflow 不再直接向群组发送。

## 发布包内容

wheel 只包含运行时包和许可证。

sdist 保留运行时源码、项目 README、CHANGELOG、LICENSE、pyproject、
setup 文件和 `docs/`，不包含以下开发或治理内容：

- `.github/`
- `examples/`
- `tests/`
- `.flake8`
- `.gitattributes`
- `.gitignore`
- `.gitleaks.baseline.json`
- `FIX-PLAN.md`

发布 workflow 会校验这些文件不会重新进入 sdist。

## GitHub Actions Runtime

CI 和发布 workflow 使用 Node 24 runtime 兼容的 Actions 主版本：

- `actions/checkout@v6`
- `actions/setup-python@v6`
- `softprops/action-gh-release@v3`

这些版本用于消除 GitHub Actions Node.js 20 deprecation 警告。

## PyPI Trusted Publisher

当前发布仍使用 `PYPI_API_TOKEN` secret。后续可迁移到 PyPI Trusted
Publisher，以减少长期 PyPI API token 的使用。

切换前需要先在 PyPI 项目设置中确认 trusted publisher 条目：

- owner/repository: `luoyanglang/bepusdt-python-sdk`
- workflow: `publish-to-pypi.yml`
- environment: 视 PyPI 配置要求决定，当前 workflow 未设置 environment

PyPI 侧配置完成前，不要移除 `PYPI_API_TOKEN` 或改成 OIDC-only 发布。
