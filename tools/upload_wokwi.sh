#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${WOKWI_RFC2217_PORT:-4000}"
remote="port:rfc2217://localhost:${port}"
staging="$(mktemp -d)"
trap 'rm -rf "$staging"' EXIT

cd "$project_root"
cp -R src/client "$staging/client"
rm -f "$staging/client/config/device.ini" "$staging/client/config/network.ini"
find "$staging/client" -type d -name __pycache__ -prune -exec rm -rf {} +
cp wokwi/device.ini "$staging/client/config/device.ini"
cp wokwi/network.ini "$staging/client/config/network.ini"
cp wokwi/main.py "$staging/client/main.py"
python -m mpremote connect "$remote" fs cp -r "$staging/client"/* :
python -m mpremote connect "$remote" reset
echo "Uploaded Message Box client and simulator harness over RFC2217 ${port}"
