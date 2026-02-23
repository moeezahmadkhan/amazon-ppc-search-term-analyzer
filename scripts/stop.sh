#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="$ROOT_DIR/.run/pids"

stop_from_pid_file() {
  local name="$1"
  local pid_file="$2"

  if [[ ! -f "$pid_file" ]]; then
    echo "[INFO] $name not started via scripts (no pid file)."
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -z "$pid" ]]; then
    rm -f "$pid_file"
    echo "[WARN] $name pid file was empty."
    return 0
  fi

  if kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    sleep 1
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill -9 "$pid" >/dev/null 2>&1 || true
      echo "[INFO] $name force-stopped (PID $pid)."
    else
      echo "[INFO] $name stopped (PID $pid)."
    fi
  else
    echo "[INFO] $name process not running (stale PID $pid)."
  fi

  rm -f "$pid_file"
}

echo "[INFO] Stopping Amazon PPC Search Term Analyzer"
stop_from_pid_file "Backend" "$PID_DIR/backend.pid"
stop_from_pid_file "Frontend" "$PID_DIR/frontend.pid"
echo "[INFO] Done."
