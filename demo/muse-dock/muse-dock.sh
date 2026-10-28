#!/bin/sh
# Muse Code at the dock: the gate's MCP server, and nothing else of the repo in its workspace.
# Usage: demo/muse-dock/muse-dock.sh [exec] [muse args...]   CBYP_MCP_ERP=0 for a dry run.
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$(dirname "$0")" || exit 1
# -c goes after the subcommand: `muse -c X exec` reads exec as a TUI prompt.
# Env values are secrets to Muse Code: each must be one whole ${VAR}, so export them first.
export CBYP_REPO="$REPO" CBYP_LANG="${CBYP_LANG:-tr}" CBYP_MCP_ERP="${CBYP_MCP_ERP:-1}"
SUB=""; [ "$1" = exec ] && { SUB=exec; shift; }
exec "${MUSE:-$HOME/.local/bin/muse}" $SUB -c "mcp_servers.cbyp={\"transport\":\"stdio\",\
\"command\":\"$REPO/.venv/bin/python\",\"args\":[\"-m\",\"cbyp.mcp_server\"],\
\"env\":{\"PYTHONPATH\":\"\${CBYP_REPO}\",\"CBYP_LANG\":\"\${CBYP_LANG}\",\"CBYP_MCP_ERP\":\"\${CBYP_MCP_ERP}\"}}" "$@"
