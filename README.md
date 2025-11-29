# Lookuply Infrastructure

Docker Compose orchestration for the Lookuply search engine ecosystem.

## Overview

This repository contains:
- **docker-compose.yml**: Complete service orchestration
- **Nginx configurations**: Reverse proxy with privacy-first headers
- **Environment templates**: `.env.example` for configuration

## Services

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | URL frontier and metadata storage |
| Redis | 6379 | Celery task queue |
| Meilisearch | 7700 | Search index |
| Coordinator | 8000 | URL frontier API |
| Celery Worker | - | Background task processing |
| AI Evaluator | 8001 | LLM page evaluation |
| Search API | 8002 | Public search API |
| Chat Frontend | 3000 | React UI |
| Nginx | 80/443 | Reverse proxy |

## Quick Start

### Prerequisites

- Docker 29.0+
- Docker Compose v2.40+
- Git 2.47+

### Setup

1. **Clone repository**:
```bash
git clone https://github.com/lookuply/infrastructure.git
cd infrastructure
```

2. **Clone component repositories** (adjacent to infrastructure):
```bash
cd ..
git clone https://github.com/lookuply/coordinator.git
git clone https://github.com/lookuply/crawler-node.git
git clone https://github.com/lookuply/search-api.git
git clone https://github.com/lookuply/ai-evaluator.git
git clone https://github.com/lookuply/chat-frontend.git
```

Directory structure:
```
lookuply/
├── infrastructure/       # This repo
├── coordinator/
├── crawler-node/
├── search-api/
├── ai-evaluator/
└── chat-frontend/
```

3. **Configure environment**:
```bash
cd infrastructure
cp .env.example .env
vim .env  # Fill in secrets
```

4. **Start services**:
```bash
docker compose up -d
```

5. **Check status**:
```bash
docker compose ps
docker compose logs -f
```

## Environment Variables

See `.env.example` for all required variables.

**Critical secrets**:
- `POSTGRES_PASSWORD`: Database password
- `MEILI_MASTER_KEY`: Meilisearch master key
- `EVAL_CRITERIA`: AI evaluation criteria (anti-gaming)

**Privacy settings** (hardcoded in docker-compose.yml):
- `LOG_USER_DATA=false`: No user data logging
- `ENABLE_ANALYTICS=false`: No analytics scripts
- `ENABLE_COOKIES=false`: No tracking cookies

## Privacy-First Design

**Zero User Tracking**:
- No IP logging (beyond rotated nginx logs)
- No query history
- No user profiles
- No cookies (except temporary rate limiting)
- No third-party analytics

**GDPR Compliance**: Achieved by not collecting any user data.

## Development

### Running individual services

```bash
# Database only
docker compose up -d postgres redis meilisearch

# Backend only
docker compose up -d coordinator search-api ai-evaluator

# Frontend only
docker compose up -d chat-frontend nginx
```

### Viewing logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f coordinator

# Last 100 lines
docker compose logs --tail=100 search-api
```

### Rebuilding after code changes

```bash
# Rebuild specific service
docker compose build coordinator
docker compose up -d coordinator

# Rebuild all
docker compose build
docker compose up -d
```

## Production Deployment

### Server Requirements

- **RAM**: 16GB minimum (Ollama LLM needs 8GB+)
- **Disk**: 150GB (index growth)
- **CPU**: 4+ cores recommended

### Hetzner Deployment

**Server**: 46.224.73.134

1. **SSH to server**:
```bash
ssh lookuply@46.224.73.134
```

2. **Clone repositories**:
```bash
mkdir -p ~/lookuply
cd ~/lookuply
git clone https://github.com/lookuply/infrastructure.git
# ... clone other repos
```

3. **Install Ollama** (for LLM):
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
```

4. **Configure and start**:
```bash
cd infrastructure
cp .env.example .env
vim .env  # Add production secrets
docker compose up -d
```

5. **Setup SSL** (Let's Encrypt):
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d lookuply.info -d www.lookuply.info

# Update nginx config (uncomment HTTPS server block)
vim nginx/conf.d/lookuply.conf

# Restart nginx
docker compose restart nginx
```

### Monitoring

```bash
# Check all services
docker compose ps

# Resource usage
docker stats

# Logs
docker compose logs -f --tail=100
```

## CI/CD

**GitHub Actions** workflows (to be added):
- `.github/workflows/test.yml`: Test all services
- `.github/workflows/deploy.yml`: Deploy to production

## Troubleshooting

### Database connection failed

```bash
# Check PostgreSQL is running
docker compose ps postgres
docker compose logs postgres

# Verify credentials
docker compose exec postgres psql -U lookuply -d lookuply
```

### Meilisearch not accessible

```bash
# Check health
curl http://localhost:7700/health

# Verify master key
docker compose logs meilisearch
```

### LLM not responding

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Verify model is downloaded
ollama list
```

### Frontend not loading

```bash
# Check if API URL is correct
docker compose logs chat-frontend

# Verify nginx config
docker compose exec nginx nginx -t
```

## Development Standards

**Test-Driven Development (TDD)**:
- All components must have tests before deployment
- Minimum 80% code coverage
- Privacy-critical paths require 100% coverage

**Git Workflow**:
- Feature branches: `feature/<description>`
- Conventional commits: `feat:`, `fix:`, `docs:`, etc.
- PR required before merge

**SOLID Principles**: Applied to all code

See [DEVELOPMENT.md](https://github.com/lookuply/project-docs/blob/master/DEVELOPMENT.md) for details.

## Architecture

See [ARCHITECTURE.md](https://github.com/lookuply/project-docs/blob/master/ARCHITECTURE.md) for full system design.

## License

MIT License - see [LICENSE](LICENSE)

## Contact

- **Email**: hello@lookuply.info
- **Docs**: https://github.com/lookuply/project-docs
- **Website**: https://lookuply.info

---

**Privacy-First | Decentralized | Open-Source**
