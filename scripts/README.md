# Infrastructure Scripts

Utility scripts for managing Lookuply infrastructure.

## Setup

### Quick Start

Initialize the entire infrastructure with one command:

```bash
bash scripts/setup.sh
```

This will:
1. Generate seed URLs
2. Start core services (postgres, redis, meilisearch, coordinator)
3. Import seed URLs via coordinator API
4. Start worker services (ai-evaluator, crawler-node)
5. Configure Meilisearch index

## Scripts

### Seed URL Management

#### `generate_seed_urls.py`
Generate quality seed URLs across multiple sources.

```bash
python3 generate_seed_urls.py
```

**Output files:**
- `seed_urls_wikipedia.txt` - Wikipedia articles (24 EU languages)
- `seed_urls_documentation.txt` - Technical documentation sites
- `seed_urls_quality.txt` - High-quality content sites

**Total:** ~298 URLs

#### `import_seed_urls.py`
Import URLs from file via Coordinator API.

```bash
# Import single file
python3 import_seed_urls.py seed_urls_wikipedia.txt

# Specify coordinator URL
python3 import_seed_urls.py seed_urls.txt http://coordinator:8000
```

**Environment variables:**
- `COORDINATOR_URL` - Coordinator API URL (default: http://localhost:8001)

**Features:**
- Batch import via `/api/v1/urls/batch`
- High priority for seed URLs
- Skips duplicates
- Returns stats: added, skipped, total

### Data Synchronization

#### `sync_to_meilisearch.py`
Sync evaluated pages from coordinator to Meilisearch.

```bash
# Use environment defaults
python3 sync_to_meilisearch.py

# Specify URLs
python3 sync_to_meilisearch.py http://coordinator:8000 http://meilisearch:7700
```

**Environment variables:**
- `COORDINATOR_URL` - Coordinator API URL (default: http://localhost:8001)
- `MEILISEARCH_URL` - Meilisearch URL (default: http://localhost:7700)
- `MEILISEARCH_MASTER_KEY` - Optional API key

**Features:**
- Fetches pages via `/api/v1/pages?status=evaluated`
- Batch indexing (100 pages per request)
- Pagination support
- Includes all page metadata: title, content, summary, language, ai_score

### Monitoring

#### `daily_stats.sh`
Generate daily statistics report via Coordinator API.

```bash
bash daily_stats.sh
```

**Environment variables:**
- `COORDINATOR_URL` - Coordinator API URL (default: http://localhost:8001)

**Reports:**
- Pages by status (pending, processing, evaluated, failed)
- Pages by depth (0, 1, 2, 3)
- Score distribution (0-100)
- Top domains (by page count)
- Languages distribution

**Requirements:**
- `jq` for JSON parsing (optional, will fallback to Python if not available)

## Architecture

All scripts use **API-based communication** via the Coordinator:

```
┌─────────────────────┐
│   Scripts           │
│                     │
│  - import_seed_urls │
│  - sync_meilisearch │
│  - daily_stats      │
└──────────┬──────────┘
           │ HTTP/REST
           ↓
┌─────────────────────┐
│   Coordinator API   │
│   (port 8001)       │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   PostgreSQL        │
│   (internal)        │
└─────────────────────┘
```

**Benefits:**
- No direct database access
- Proper API boundaries
- Scalable and secure
- Works with deployed infrastructure

## Automation

### Cron Jobs

Add to crontab for automated operations:

```bash
# Daily stats at 9 AM
0 9 * * * cd /path/to/infrastructure && bash scripts/daily_stats.sh >> logs/daily_stats.log 2>&1

# Sync to Meilisearch every hour
0 * * * * cd /path/to/infrastructure && python3 scripts/sync_to_meilisearch.py >> logs/sync.log 2>&1
```

### Docker Scheduler

Alternatively, use a scheduler container in docker-compose.yml:

```yaml
scheduler:
  image: mcuadros/ofelia:latest
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - ./scripts:/scripts:ro
  environment:
    - COORDINATOR_URL=http://coordinator:8000
  labels:
    ofelia.job-exec.daily-stats.schedule: "0 9 * * *"
    ofelia.job-exec.daily-stats.command: "bash /scripts/daily_stats.sh"
    ofelia.job-exec.sync.schedule: "0 * * * *"
    ofelia.job-exec.sync.command: "python3 /scripts/sync_to_meilisearch.py"
```

## Troubleshooting

### Cannot connect to coordinator

```bash
# Check if coordinator is running
docker-compose ps coordinator

# Check coordinator logs
docker-compose logs coordinator

# Test health endpoint
curl http://localhost:8001/health
```

### Meilisearch indexing fails

```bash
# Check Meilisearch status
curl http://localhost:7700/health

# Check index exists
curl http://localhost:7700/indexes/pages

# Verify API key (if set)
echo $MEILISEARCH_MASTER_KEY
```

### Import seed URLs fails

```bash
# Verify file exists
ls -la seed_urls_*.txt

# Check URL format (one URL per line, no extra whitespace)
cat seed_urls_wikipedia.txt | head

# Test coordinator API manually
curl -X POST http://localhost:8001/api/v1/urls/batch \
  -H "Content-Type: application/json" \
  -d '{"urls":[{"url":"https://example.com","priority":"high","depth":0}]}'
```

## Development

### Testing Scripts Locally

```bash
# Set environment variables
export COORDINATOR_URL=http://localhost:8001
export MEILISEARCH_URL=http://localhost:7700

# Run scripts
python3 import_seed_urls.py test_urls.txt
python3 sync_to_meilisearch.py
bash daily_stats.sh
```

### Adding New Scripts

1. Create script in `scripts/` directory
2. Make executable: `chmod +x script.sh`
3. Use environment variables for configuration
4. Follow API-based architecture (no direct DB access)
5. Add documentation to this README
6. Test locally before committing

## License

Part of the Lookuply project.
