#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="aax-web"

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is required. Please install tmux." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required." >&2
  exit 1
fi

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "Session '$SESSION_NAME' already exists. Attach with: tmux attach -t $SESSION_NAME"
  exit 0
fi

# Start session and run the app from project root
PROJECT_ROOT="$(pwd)"
CMD="cd \"$PROJECT_ROOT\" && python3 web/app.py"

tmux new-session -d -s "$SESSION_NAME" "$CMD"
echo "Started web app in tmux session '$SESSION_NAME'. Attach with: tmux attach -t $SESSION_NAME"
