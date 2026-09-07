#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scenarios=(
  wokwi/scenarios/boot-and-recovery.test.yaml
  wokwi/scenarios/clockwise.test.yaml
  wokwi/scenarios/counter-clockwise.test.yaml
  wokwi/scenarios/menu-scroll.test.yaml
)

command -v wokwi-cli >/dev/null || {
  echo "BLOCKED: wokwi-cli is not installed" >&2
  exit 2
}
test -n "${WOKWI_CLI_TOKEN:-}" || {
  echo "BLOCKED: WOKWI_CLI_TOKEN is not set" >&2
  exit 2
}

cd "$project_root"
wokwi-cli lint
for scenario in "${scenarios[@]}"; do
  wokwi-cli . --scenario "$scenario" --timeout 120000 &
  cli_pid=$!
  uploaded=0
  for _ in $(seq 1 40); do
    if python -m mpremote connect port:rfc2217://localhost:4000 fs ls >/dev/null 2>&1; then
      ./tools/upload_wokwi.sh
      uploaded=1
      break
    fi
    sleep 0.5
  done
  if [[ "$uploaded" != 1 ]]; then
    kill "$cli_pid" 2>/dev/null || true
    wait "$cli_pid" 2>/dev/null || true
    echo "BLOCKED: RFC2217 simulator did not become ready" >&2
    exit 3
  fi
  wait "$cli_pid"
done
