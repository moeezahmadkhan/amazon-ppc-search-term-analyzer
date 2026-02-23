#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
PID_DIR="$RUN_DIR/pids"
LOG_DIR="$RUN_DIR/logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

load_env_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$file"
    set +a
  fi
}

yaml_get() {
  local key="$1"
  local yaml_file="$2"
  awk -F': *' -v k="$key" '$1 == k {print $2; exit}' "$yaml_file" | sed 's/"//g' | sed "s/'//g"
}

is_pid_running() {
  local pid="$1"
  if [[ -z "$pid" ]]; then
    return 1
  fi
  kill -0 "$pid" >/dev/null 2>&1
}

port_in_use() {
  local port="$1"
  python3 - <<PY
import socket
s = socket.socket()
s.settimeout(0.5)
result = s.connect_ex(("127.0.0.1", int("$port")))
s.close()
print("1" if result == 0 else "0")
PY
}

APP_CONFIG_PATH_DEFAULT="config/app.yaml"
if [[ -f "$ROOT_DIR/.env" ]]; then
  load_env_file "$ROOT_DIR/.env"
fi
APP_CONFIG_PATH="${APP_CONFIG_PATH:-$APP_CONFIG_PATH_DEFAULT}"
CONFIG_FILE="$ROOT_DIR/$APP_CONFIG_PATH"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "[ERROR] Config file not found: $CONFIG_FILE"
  echo "Create it from config/app.yaml.example"
  exit 1
fi

# Load scoped env files after root env so scoped values can override.
load_env_file "$ROOT_DIR/backend/.env"
load_env_file "$ROOT_DIR/frontend/.env"

BACKEND_HOST="${BACKEND_HOST:-$(yaml_get backend_host "$CONFIG_FILE")}"
BACKEND_PORT="${BACKEND_PORT:-$(yaml_get backend_port "$CONFIG_FILE")}"
BACKEND_CORS_ORIGINS="${BACKEND_CORS_ORIGINS:-$(yaml_get backend_cors_origins "$CONFIG_FILE")}"

FRONTEND_HOST="${FRONTEND_HOST:-$(yaml_get frontend_host "$CONFIG_FILE")}"
FRONTEND_PORT="${FRONTEND_PORT:-$(yaml_get frontend_port "$CONFIG_FILE")}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-$(yaml_get frontend_public_api_url "$CONFIG_FILE")}"
OPENAI_MODEL="${OPENAI_MODEL:-$(yaml_get openai_model "$CONFIG_FILE")}"

BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

echo "[INFO] Starting Amazon PPC Search Term Analyzer"
echo "[INFO] Config: $CONFIG_FILE"

# Start backend
if [[ -f "$BACKEND_PID_FILE" ]] && is_pid_running "$(cat "$BACKEND_PID_FILE")"; then
  echo "[INFO] Backend already running with PID $(cat "$BACKEND_PID_FILE")"
else
  if [[ "$(port_in_use "$BACKEND_PORT")" == "1" ]]; then
    echo "[WARN] Port $BACKEND_PORT already in use. Skipping backend start."
  else
    (
      cd "$ROOT_DIR/backend"
      BACKEND_CORS_ORIGINS="$BACKEND_CORS_ORIGINS" \
      OPENAI_MODEL="$OPENAI_MODEL" \
      nohup uvicorn app.main:app \
        --host "$BACKEND_HOST" \
        --port "$BACKEND_PORT" \
        > "$LOG_DIR/backend.log" 2>&1 &
      echo $! > "$BACKEND_PID_FILE"
    )
    echo "[INFO] Backend started on http://$BACKEND_HOST:$BACKEND_PORT (PID $(cat "$BACKEND_PID_FILE"))"
  fi
fi

# Start frontend
if [[ -f "$FRONTEND_PID_FILE" ]] && is_pid_running "$(cat "$FRONTEND_PID_FILE")"; then
  echo "[INFO] Frontend already running with PID $(cat "$FRONTEND_PID_FILE")"
else
  if [[ "$(port_in_use "$FRONTEND_PORT")" == "1" ]]; then
    echo "[WARN] Port $FRONTEND_PORT already in use. Skipping frontend start."
  else
    (
      cd "$ROOT_DIR/frontend"
      NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL" \
      nohup npm run dev -- --hostname "$FRONTEND_HOST" --port "$FRONTEND_PORT" \
        > "$LOG_DIR/frontend.log" 2>&1 &
      echo $! > "$FRONTEND_PID_FILE"
    )
    echo "[INFO] Frontend started on http://$FRONTEND_HOST:$FRONTEND_PORT (PID $(cat "$FRONTEND_PID_FILE"))"
  fi
fi

echo
echo "[INFO] Endpoints"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Backend : http://localhost:$BACKEND_PORT"
echo "[INFO] Logs"
echo "  $LOG_DIR/backend.log"
echo "  $LOG_DIR/frontend.log"
