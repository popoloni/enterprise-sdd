#!/usr/bin/env bash
# lint-agent-size.sh — Check agent files against their declared size-tier budget.
# Usage: ./lint-agent-size.sh [agents-directory]
#
# Exits 0 if all agents are within budget, 1 if violations are found.

set -euo pipefail

AGENTS_DIR="${1:-.github/agents}"
VIOLATIONS=0

# Default tier budgets (lines)
declare -A TIER_BUDGET=(
  [compact]=200
  [standard]=400
  [extended]=600
)

echo "=== Agent Size Lint ==="
echo "Scanning: ${AGENTS_DIR}"
echo ""

printf "%-40s %6s  %-10s %6s  %s\n" "Agent" "Lines" "Tier" "Budget" "Status"
printf "%-40s %6s  %-10s %6s  %s\n" "-----" "-----" "----" "------" "------"

for agent_file in "${AGENTS_DIR}"/*.agent.md; do
  [ -f "$agent_file" ] || continue

  filename=$(basename "$agent_file")
  line_count=$(wc -l < "$agent_file")

  # Extract size-tier from YAML frontmatter
  tier=$(grep -m1 'size-tier:' "$agent_file" 2>/dev/null | sed 's/.*size-tier:\s*//' | tr -d '[:space:]' || true)

  # Default to standard if not declared
  if [ -z "$tier" ]; then
    tier="standard"
  fi

  budget=${TIER_BUDGET[$tier]:-400}

  if [ "$line_count" -gt "$budget" ]; then
    status="❌ OVER"
    VIOLATIONS=$((VIOLATIONS + 1))
  else
    status="✅ OK"
  fi

  printf "%-40s %6d  %-10s %6d  %s\n" "$filename" "$line_count" "$tier" "$budget" "$status"
done

echo ""
if [ "$VIOLATIONS" -gt 0 ]; then
  echo "⚠️  ${VIOLATIONS} agent(s) exceed their size budget."
  echo "Refactor: extract tables into .instructions.md or split modes into separate agents."
  exit 1
else
  echo "✅ All agents within size budget."
  exit 0
fi
