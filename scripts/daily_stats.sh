#!/bin/bash
# Daily statistics report via Coordinator API

set -euo pipefail

# Configuration
COORDINATOR_URL="${COORDINATOR_URL:-http://localhost:8001}"
STATS_API="${COORDINATOR_URL}/api/v1/stats"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "📊 Lookuply Daily Statistics - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"
echo

# Check if coordinator is reachable
if ! curl -sf "${COORDINATOR_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to coordinator at ${COORDINATOR_URL}${NC}"
    echo "   Make sure the coordinator service is running"
    exit 1
fi

echo -e "${GREEN}✓ Coordinator reachable${NC}"
echo

# Fetch stats from API
echo "Fetching statistics from ${STATS_API}..."
STATS=$(curl -sf "${STATS_API}" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to fetch statistics${NC}"
    exit 1
fi

echo

# Parse and display stats using jq
if command -v jq &> /dev/null; then
    echo "📈 Pages by Status:"
    echo "$STATS" | jq -r '.pages_by_status | to_entries[] | "   \(.key): \(.value)"'
    echo

    echo "🌳 Pages by Depth:"
    echo "$STATS" | jq -r '.pages_by_depth | to_entries[] | "   Depth \(.key): \(.value)"'
    echo

    echo "⭐ Score Distribution:"
    echo "$STATS" | jq -r '.score_distribution | to_entries[] | "   \(.key): \(.value)"'
    echo

    echo "🌐 Top Domains:"
    echo "$STATS" | jq -r '.top_domains[] | "   \(.domain): \(.count) pages"'
    echo

    echo "🗣️  Languages:"
    echo "$STATS" | jq -r '.languages | to_entries[] | "   \(.key): \(.value)"'
    echo
else
    # Fallback if jq not available - just show raw JSON
    echo "⚠️  jq not installed, showing raw JSON:"
    echo "$STATS" | python3 -m json.tool
    echo
fi

echo "================================================================"
echo "✅ Statistics report complete"
