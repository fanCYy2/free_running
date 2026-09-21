#!/bin/bash
# macOS 一键启动脚本
#
# macOS 上不再需要 root：pymobiledevice3 11.x 会通过系统的 remotepairingd
# 借用 Apple 自己的隧道（Xcode 用的就是它），不用我们自己创建 tun 设备。

set -euo pipefail

cd "$(dirname "$0")"

VENV="venv"
PY="$VENV/bin/python"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "run.sh 仅适用于 macOS，Windows 请参考 README.md" >&2
    exit 1
fi

# 找一个 3.10 以上的 python3
find_python() {
    local candidate
    for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1 \
            && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

if [[ ! -x "$PY" ]]; then
    echo "==> 创建虚拟环境 $VENV"
    if ! BOOTSTRAP_PY="$(find_python)"; then
        echo "未找到 Python 3.10 或更高版本，请先安装：brew install python" >&2
        exit 1
    fi
    echo "    使用 $BOOTSTRAP_PY"
    "$BOOTSTRAP_PY" -m venv "$VENV"
fi

# 依赖不全或版本过旧时才装，避免每次启动都联网
if ! "$PY" -c '
import sys
from importlib.metadata import version
from packaging.version import Version
import yaml, geopy, coloredlogs          # noqa: F401
sys.exit(0 if Version(version("pymobiledevice3")).major >= 11 else 1)
' >/dev/null 2>&1; then
    echo "==> 安装依赖"
    "$PY" -m pip install --upgrade pip
    "$PY" -m pip install -r requirements.txt
fi

echo "==> 启动（macOS 无需 root）"
echo "    结束请按 Ctrl+C，不要直接关闭窗口，否则定位无法恢复"

exec "$PY" main.py "$@"
