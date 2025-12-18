#!/bin/bash
# Lookuply Infrastructure Setup Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🚀 Lookuply Infrastructure Setup"
echo "================================================================"
echo

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    echo "   Please install Docker Compose first"
    exit 1
fi

# Use 'docker compose' or 'docker-compose' based on availability
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${GREEN}✓ Docker Compose found${NC}"
echo

# Step 1: Generate seed URLs
echo "📝 Step 1: Generate seed URLs"
echo "----------------------------------------------------------------"

if [ ! -f "scripts/generate_seed_urls.py" ]; then
    echo -e "${RED}❌ generate_seed_urls.py not found${NC}"
    exit 1
fi

cd scripts
python3 generate_seed_urls.py
cd ..

echo -e "${GREEN}✓ Seed URLs generated${NC}"
echo

# Step 2: Start core services
echo "🐳 Step 2: Start core services (postgres, redis, meilisearch, coordinator)"
echo "----------------------------------------------------------------"

$DOCKER_COMPOSE up -d postgres redis meilisearch coordinator

echo -e "${YELLOW}⏳ Waiting for services to be ready (30s)...${NC}"
sleep 30

# Check if coordinator is up
if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Coordinator is ready${NC}"
else
    echo -e "${RED}❌ Coordinator not responding${NC}"
    echo "   Check logs: $DOCKER_COMPOSE logs coordinator"
    exit 1
fi

echo

# Step 3: Import seed URLs
echo "📥 Step 3: Import seed URLs"
echo "----------------------------------------------------------------"

for seed_file in scripts/seed_urls_*.txt; do
    if [ -f "$seed_file" ]; then
        echo "Importing $(basename $seed_file)..."
        python3 scripts/import_seed_urls.py "$seed_file" http://localhost:8001
    fi
done

echo -e "${GREEN}✓ Seed URLs imported${NC}"
echo

# Step 4: Start worker services
echo "⚙️  Step 4: Start worker services (ai-evaluator, crawler-node)"
echo "----------------------------------------------------------------"

$DOCKER_COMPOSE up -d ai-evaluator crawler-node

echo -e "${GREEN}✓ Worker services started${NC}"
echo

# Step 5: Configure Meilisearch
echo "🔍 Step 5: Configure Meilisearch index"
echo "----------------------------------------------------------------"

# Wait for Meilisearch
sleep 5

# Create index with settings
MEILISEARCH_URL="http://localhost:7700"
MEILISEARCH_KEY="${MEILISEARCH_MASTER_KEY:-}"

curl -X POST "${MEILISEARCH_URL}/indexes" \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "pages",
    "primaryKey": "id"
  }' 2>/dev/null || true

# Set ranking rules
curl -X PATCH "${MEILISEARCH_URL}/indexes/pages/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "rankingRules": [
      "words",
      "typo",
      "proximity",
      "attribute",
      "sort",
      "exactness",
      "ai_score:desc"
    ],
    "searchableAttributes": [
      "title",
      "content",
      "summary",
      "url"
    ],
    "filterableAttributes": [
      "language",
      "ai_score",
      "depth"
    ],
    "sortableAttributes": [
      "ai_score",
      "evaluated_at"
    ]
  }' 2>/dev/null

echo -e "${GREEN}✓ Meilisearch configured${NC}"
echo

# Summary
echo "================================================================"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo
echo "Services running:"
$DOCKER_COMPOSE ps
echo
echo "Next steps:"
echo "  1. Check logs: $DOCKER_COMPOSE logs -f"
echo "  2. View stats: bash scripts/daily_stats.sh"
echo "  3. Sync to search: python3 scripts/sync_to_meilisearch.py"
echo
echo "URLs:"
echo "  Coordinator: http://localhost:8001"
echo "  Meilisearch: http://localhost:7700"
echo
