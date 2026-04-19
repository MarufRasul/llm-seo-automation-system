#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "$0")" && pwd)/.."

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export AUTO_RUN_MODE=lg_daily
PYTHONUNBUFFERED=1 python -u llm_seo_system/auto_runner.py
