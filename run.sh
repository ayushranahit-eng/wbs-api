#!/usr/bin/env bash
set -u

BASE_URL="${BASE_URL:-http://localhost:8000/deep-scan}"
ASSET_BASE_URL="${SCAN_ASSET_BASE:-http://localhost:8000/deep-scan/v3}"
RUNNER_DIR="${SCAN_RUNNER_DIR:-${TMPDIR:-/tmp}/scan-sh-runner.$$}"
SCAN_ARGS="${SCAN_ARGS:---fail-on never --clean}"
SKIP_SEMGREP_INSTALL="${SKIP_SEMGREP_INSTALL:-0}"

log() {
  printf '[scan.sh installer] %s
' "$*" >&2
}

have() {
  command -v "$1" >/dev/null 2>&1
}

find_python() {
  for candidate in python3 python; do
    if have "$candidate" && "$candidate" -c "import sys" >/dev/null 2>&1; then
      printf '%s
' "$candidate"
      return 0
    fi
  done
  return 1
}

download() {
  url="$1"
  dest="$2"
  if have curl; then
    curl -fsSL "$url" -o "$dest"
    return $?
  fi
  if have wget; then
    wget -qO "$dest" "$url"
    return $?
  fi
  "$PYTHON_BIN" - "$url" "$dest" <<'PY'
import sys
import urllib.request
urllib.request.urlretrieve(sys.argv[1], sys.argv[2])
PY
}

PYTHON_BIN="$(find_python || true)"
if [ -z "$PYTHON_BIN" ]; then
  log "Python 3 is required but was not found."
  exit 2
fi

rm -rf -- "$RUNNER_DIR"
mkdir -p "$RUNNER_DIR"
download "$ASSET_BASE_URL/scan.sh" "$RUNNER_DIR/scan.sh"
download "$ASSET_BASE_URL/merge_report.py" "$RUNNER_DIR/merge_report.py"
download "$ASSET_BASE_URL/find_exposed_files.sh" "$RUNNER_DIR/find_exposed_files.sh"
chmod +x "$RUNNER_DIR/scan.sh" "$RUNNER_DIR/find_exposed_files.sh"

if ! have semgrep && [ "$SKIP_SEMGREP_INSTALL" != "1" ]; then
  log "Semgrep not found. Trying user install with pip."
  install_log="$RUNNER_DIR/semgrep-install.log"
  if "$PYTHON_BIN" -m pip --version >/dev/null 2>&1 || "$PYTHON_BIN" -m ensurepip --upgrade >/dev/null 2>&1; then
    pip_install_args="--user"
    if [ -n "${VIRTUAL_ENV:-}" ]; then
      pip_install_args=""
      log "Python virtualenv detected. Installing Semgrep into the active virtualenv."
    fi
    if ! PIP_DISABLE_PIP_VERSION_CHECK=1 "$PYTHON_BIN" -m pip install $pip_install_args semgrep >"$install_log" 2>&1; then
      log "Semgrep install failed; showing the last lines from $install_log"
      tail -n 20 "$install_log" >&2 || true
      log "Scan will continue with built-in checks."
    fi
  else
    log "pip is not available for $PYTHON_BIN; scan will continue with built-in checks."
  fi
  export PATH="$HOME/.local/bin:$PATH"
fi

log "Running scan in $(pwd)"
BASE_URL="$BASE_URL" SCAN_ASSET_BASE="$ASSET_BASE_URL" "$RUNNER_DIR/scan.sh" $SCAN_ARGS
SCAN_EXIT=$?

rm -rf -- "$RUNNER_DIR"
exit "$SCAN_EXIT"
