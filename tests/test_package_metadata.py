"""打包元数据测试"""

from email.parser import Parser
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def test_build_uses_setuptools_scm_version(tmp_path):
    """构建产物版本应来自 setuptools_scm，而不是 setup.py 写死版本"""
    project_root = Path(__file__).resolve().parents[1]
    generated_version = project_root / "bepusdt" / "_version.py"
    stale_build_package = project_root / "build" / "lib" / "bepusdt"
    original_version = generated_version.read_bytes() if generated_version.exists() else None
    env = os.environ.copy()
    env["SETUPTOOLS_SCM_PRETEND_VERSION"] = "9.8.7"
    stale_build_package.mkdir(parents=True, exist_ok=True)
    (stale_build_package / "__init__.py").write_text("# stale build artifact\n", encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "build", "--wheel", "--outdir", str(tmp_path)],
            check=True,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    finally:
        if original_version is None:
            generated_version.unlink(missing_ok=True)
        else:
            generated_version.write_bytes(original_version)
        shutil.rmtree(project_root / "build", ignore_errors=True)

    wheels = list(tmp_path.glob("bepusdt-9.8.7-*.whl"))
    assert wheels, result.stdout + result.stderr

    with zipfile.ZipFile(wheels[0]) as wheel:
        wheel_files = wheel.namelist()
        metadata = wheel.read("bepusdt-9.8.7.dist-info/METADATA").decode("utf-8")

    assert not any(name.startswith("build/") for name in wheel_files)
    assert "Version: 9.8.7" in metadata
    assert "project.license as a TOML table is deprecated" not in result.stderr
    assert "License classifiers are deprecated" not in result.stderr

    parsed_metadata = Parser().parsestr(metadata)
    assert parsed_metadata["License-Expression"] == "MIT"
    assert parsed_metadata["License"] is None
    assert "LICENSE" in parsed_metadata.get_all("License-File", [])
    assert "License :: OSI Approved :: MIT License" not in parsed_metadata.get_all("Classifier", [])
