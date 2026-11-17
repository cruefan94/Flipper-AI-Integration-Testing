#!/bin/sh
# Offline-only llama.cpp server bridge for the Flipper AI Android Satellite.
# The Android app calls 127.0.0.1:9931/v1/chat/completions with model flipper-local.
# No downloads, remote access, background installation or hardware commands.
set -eu

usage() {
  echo "Usage: sh termux/start_flipper_llama.sh start /absolute/path/model.gguf" >&2
  echo "       sh termux/start_flipper_llama.sh status" >&2
  exit 2
}

case "${1:-}" in
  status)
    [ "$#" -eq 1 ] || usage
    if ! command -v curl >/dev/null 2>&1; then
      echo "curl is not installed in Termux; run: pkg install curl" >&2
      exit 1
    fi
    code="$(curl --noproxy '*' --silent --show-error --max-time 4 \
      --output /dev/null --write-out '%{http_code}' \
      http://127.0.0.1:9931/health 2>/dev/null || true)"
    case "$code" in
      200) echo "Local llama.cpp health endpoint reachable on 127.0.0.1:9931 (inference not yet verified)." ;;
      503) echo "Local llama.cpp endpoint is responding but model may still be loading."; exit 1 ;;
      *) echo "No ready local server at 127.0.0.1:9931 (HTTP ${code:-000})."; exit 1 ;;
    esac
    ;;
  start)
    [ "$#" -eq 2 ] || usage
    model="$2"
    case "$model" in
      /*.gguf) ;;
      *) echo "Use an absolute path to an existing .gguf file in Termux." >&2; exit 2 ;;
    esac
    if [ ! -f "$model" ]; then
      echo "Model file not found; install your chosen GGUF weights separately." >&2
      exit 1
    fi
    if command -v llama-server >/dev/null 2>&1; then
      server="$(command -v llama-server)"
    elif [ -x "$HOME/llama.cpp/build/bin/llama-server" ]; then
      server="$HOME/llama.cpp/build/bin/llama-server"
    else
      echo "llama-server is not installed. Build/install a compatible official llama.cpp server in Termux." >&2
      echo "See: https://github.com/ggml-org/llama.cpp/tree/master/tools/server" >&2
      exit 1
    fi
    echo "Starting local CPU-only llama.cpp at 127.0.0.1:9931; no LAN listening."
    echo "Keep this Termux session active. Use the app's TEST LLAMA.CPP SERVER button."
    exec "$server" --model "$model" --host 127.0.0.1 --port 9931 \
      --alias flipper-local --ctx-size 2048 --gpu-layers 0 --no-webui
    ;;
  *) usage ;;
esac
