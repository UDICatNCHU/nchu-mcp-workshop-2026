#!/usr/bin/env bash
# Push workshop materials to Google Drive via rclone.
#
# One-time setup (interactive, browser auth):
#   rclone config
#     n  →  name: gdrive
#     storage: drive
#     client_id/secret: blank (use rclone defaults)
#     scope: 1   (drive — full access)
#     advanced/auto-config: defaults
#     team drive: n
#
# After setup, run after regenerating any .pptx:
#   ./tools/sync-to-drive.sh

set -euo pipefail

REMOTE="${REMOTE:-gdrive}"
TARGET="${TARGET:-NCHU MCP Workshop 2026}"
RCLONE="${RCLONE:-rclone}"

cd "$(dirname "$0")/.."

if ! command -v "$RCLONE" >/dev/null 2>&1; then
  echo "ERROR: rclone not found. Install: curl https://rclone.org/install.sh | sudo bash" >&2
  echo "Or set RCLONE=/path/to/rclone if installed elsewhere." >&2
  exit 1
fi

if ! "$RCLONE" listremotes | grep -qx "${REMOTE}:"; then
  echo "ERROR: rclone remote '${REMOTE}' not configured. Run: rclone config" >&2
  exit 1
fi

echo "→ syncing workshop materials to ${REMOTE}:${TARGET}/"

"$RCLONE" copy . "${REMOTE}:${TARGET}" \
  --include "*.pptx" \
  --include "*.html" \
  --include "*.md" \
  --exclude "node_modules/**" \
  --exclude "mini-project/**" \
  --exclude ".venv/**" \
  --exclude ".git/**" \
  --progress \
  --transfers 4 \
  --checkers 8

echo "✓ done. View: https://drive.google.com/drive/folders/1IKYuPgYnAKEjpBESe5ULTwYldRWlgmSq"
