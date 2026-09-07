#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
staging="$(mktemp -d)"
trap 'rm -rf "$staging"' EXIT

cd "$project_root"
for config_file in src/client/config/device.ini src/client/config/network.ini; do
  if [[ ! -f "$config_file" ]]; then
    echo "Missing ignored device configuration: $config_file" >&2
    exit 2
  fi
done

cp -R src/client "$staging/client"
find "$staging/client" -type d -name __pycache__ -prune -exec rm -rf {} +
python -m mpremote connect auto fs cp -r "$staging/client"/* :
python -m mpremote connect auto reset
echo "Uploaded Message Box application over USB without flashing firmware"
