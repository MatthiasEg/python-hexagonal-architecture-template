#!/usr/bin/env bash
# PostToolUse hook — format and autofix only the Python file that was just edited.
#
# Claude Code passes the tool payload as JSON on stdin; we read the edited file path
# from it and run ruff on that single file. Non-Python edits are ignored. Failures are
# swallowed so the hook never blocks the edit — `uv run poe check` is the real gate.
set -euo pipefail

file="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)"

case "$file" in
  *.py)
    uv run ruff format "$file" >/dev/null 2>&1 || true
    uv run ruff check --fix "$file" >/dev/null 2>&1 || true
    ;;
esac
