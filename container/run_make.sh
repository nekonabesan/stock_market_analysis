#!/usr/bin/env bash
set -eu -o pipefail

# run_make.sh
# Makefile を変更せずに、実行環境の差分を吸収して `make -C container <target>` を実行する補助スクリプト
# - デフォルト target: build
# - 環境準備:
#   * PATH に $HOME/bin を先頭追加（既に作成した docker wrapper を優先）
#   * DOCKER_BUILDKIT を有効化
#   * オプションで FORCE_AMD64=1 を指定すると DOCKER_DEFAULT_PLATFORM=linux/amd64 をセット
#   * colima コンテキストが選択されていて colima が停止している場合、自動起動を試みる

TARGET=${1:-build}
shift || true

# 前置 PATH（~/bin を先頭に）
export PATH="$HOME/bin:$PATH"
export DOCKER_BUILDKIT=1

if [ "${FORCE_AMD64:-0}" = "1" ]; then
  export DOCKER_DEFAULT_PLATFORM=linux/amd64
  echo "[run_make] FORCING build platform: $DOCKER_DEFAULT_PLATFORM"
fi

# If docker context is colima and colima exists, ensure it's running (non-interactive start)
if command -v docker >/dev/null 2>&1; then
  if docker context ls --format "{{.Name}}\t{{.Current}}" 2>/dev/null | grep -q '^colima\t\*' ; then
    if command -v colima >/dev/null 2>&1; then
      # check status
      COLIMA_STATUS=$(colima status --json 2>/dev/null || true)
      if ! echo "$COLIMA_STATUS" | grep -q 'colima is running' 2>/dev/null; then
        echo "[run_make] Colima context detected but Colima not running; attempting to start (may take a while)..."
        colima start || {
          echo "[run_make] colima start failed; continue and let make report errors" >&2
        }
      fi
    fi
  fi
fi

# Print a short environment summary
echo "[run_make] PATH=$PATH"
if command -v docker >/dev/null 2>&1; then
  echo "[run_make] docker version: $(docker --version 2>/dev/null || true)"
  if docker compose version >/dev/null 2>&1; then
    echo "[run_make] docker compose: $(docker compose version 2>/dev/null || true)"
  elif command -v docker-compose >/dev/null 2>&1; then
    echo "[run_make] docker-compose: $(docker-compose --version 2>/dev/null || true)"
  else
    echo "[run_make] WARNING: neither 'docker compose' nor 'docker-compose' available" >&2
  fi
fi

# Execute make in container directory with any additional args forwarded
echo "[run_make] Running: PATH=... make -C container $TARGET $*"
PATH="$HOME/bin:$PATH" make -C container "$TARGET" "$@"

exit $?
