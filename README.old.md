# Lookuply Infrastructure

**Infrastructure as Code for privacy-first search engine**

Part of the [Lookuply](https://github.com/lookuply) open-source search engine project.

---

## Overview

This repository contains all infrastructure configuration, deployment scripts, and documentation for running Lookuply in production. Built with Docker Compose and ready for Kubernetes scaling.

### Key Features

- **Docker Compose**: Easy local development and small-scale deployment
- **Kubernetes Ready**: Helm charts for production scaling
- **Infrastructure as Code**: Reproducible, version-controlled infrastructure
- **Monitoring Stack**: Prometheus + Grafana dashboards
- **Automated Backups**: PostgreSQL and configuration backups
- **Security Hardened**: Firewall rules, SSL/TLS, fail2ban

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Cloudflare CDN                   │
│                  (DNS + DDoS Protection)            │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│                  Hetzner Server                     │
│                 (8 vCPU, 16GB RAM)                  │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Nginx   │  │ Certbot  │  │   UFW    │         │
│  │  Proxy   │  │   SSL    │  │ Firewall │         │
│  └────┬─────┘  └──────────┘  └──────────┘         │
│       │                                             │
│  ┌────┴──────────────────────────────────────┐     │
│  │           Docker Compose                  │     │
│  ├───────────────────────────────────────────┤     │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐  │     │
│  │ │OpenSearch│ │  Qdrant  │ │PostgreSQL│  │     │
│  │ └──────────┘ └──────────┘ └──────────┘  │     │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐  │     │
│  │ │  Redis   │ │  Ollama  │ │ Frontend │  │     │
│  │ └──────────┘ └──────────┘ └──────────┘  │     │
│  │ ┌──────────┐ ┌──────────┐               │     │
│  │ │  Crawler │ │Search API│               │     │
│  │ └──────────┘ └──────────┘               │     │
│  └───────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

---

## Technology Stack

- **Hosting**: Hetzner Cloud (VPS/Dedicated)
- **CDN**: Cloudflare (Free tier)
- **Containers**: Docker + Docker Compose
- **Orchestration**: Kubernetes (optional, for scaling)
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt via Certbot
- **Firewall**: UFW + fail2ban
- **Monitoring**: Prometheus + Grafana
- **Backups**: Automated scripts

---

## Quick Start

### Prerequisites

```bash
- Linux server (Ubuntu 22.04+ or Debian 12+)
- Docker & Docker Compose installed
- Domain name pointed to server
- Cloudflare account (recommended)
```

### Initial Setup

```bash
# Clone repository
git clone https://github.com/lookuply/infrastructure.git
cd infrastructure

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Run setup script
./scripts/setup.sh

# Start all services
docker-compose up -d
```

---

## Project Structure

```
infrastructure/
├── docker/
│   ├── docker-compose.yml        # Main compose file
│   ├── docker-compose.prod.yml   # Production overrides
│   └── docker-compose.dev.yml    # Development overrides
├── nginx/
│   ├── conf.d/                   # Nginx configs
│   ├── ssl/                      # SSL certificates
│   └── nginx.conf                # Main Nginx config
├── kubernetes/
│   ├── charts/                   # Helm charts
│   ├── deployments/              # K8s deployments
│   └── services/                 # K8s services
├── scripts/
│   ├── setup.sh                  # Initial server setup
│   ├── backup.sh                 # Backup script
│   ├── restore.sh                # Restore script
│   └── deploy.sh                 # Deployment script
├── monitoring/
│   ├── prometheus/               # Prometheus config
│   └── grafana/                  # Grafana dashboards
└── docs/
    ├── SETUP.md                  # Setup guide
    ├── DEPLOYMENT.md             # Deployment guide
    └── TROUBLESHOOTING.md        # Common issues
```

---

## Services

### Core Services

| Service | Port | Description |
|---------|------|-------------|
| OpenSearch | 9200 | Full-text search engine |
| Qdrant | 6333 | Vector database |
| PostgreSQL | 5432 | Relational database |
| Redis | 6379 | Cache & queue |

### Application Services

| Service | Port | Description |
|---------|------|-------------|
| Search API | 8000 | REST API |
| Frontend | 3000 | Web interface |
| Crawler | - | Background service |

### Infrastructure Services

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80, 443 | Reverse proxy |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Monitoring dashboards |
| Ollama | 11434 | LLM inference |

---

## Configuration

### Environment Variables

```bash
# Domain
DOMAIN=lookuply.info
API_DOMAIN=api.lookuply.info
DOCS_DOMAIN=docs.lookuply.info

# Database
POSTGRES_USER=lookuply
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=lookuply

# OpenSearch
OPENSEARCH_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>

# API Keys
API_SECRET_KEY=<random-key>

# Email (for Let's Encrypt)
LETSENCRYPT_EMAIL=hello@lookuply.info
```

### Resource Limits

```yaml
# docker-compose.yml
services:
  opensearch:
    mem_limit: 4g
    cpus: 2

  postgres:
    mem_limit: 2g
    cpus: 1

  qdrant:
    mem_limit: 4g
    cpus: 2
```

---

## Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or use deploy script
./scripts/deploy.sh production
```

### SSL Setup

```bash
# Initial certificate
sudo certbot --nginx -d lookuply.info -d www.lookuply.info

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

---

## Monitoring

### Prometheus Metrics

Access at: `http://localhost:9090`

Key metrics:
- API response time
- Search queries per second
- Database connections
- Disk usage
- Memory usage

### Grafana Dashboards

Access at: `http://localhost:3001`

Pre-configured dashboards:
- System Overview
- API Performance
- Search Metrics
- Database Health

---

## Backup & Restore

### Automated Backups

```bash
# Backup script runs daily via cron
0 2 * * * /opt/lookuply/scripts/backup.sh

# Manual backup
./scripts/backup.sh

# Backups stored in /opt/lookuply/backups/
```

### Restore from Backup

```bash
# List backups
ls -lh /opt/lookuply/backups/

# Restore specific backup
./scripts/restore.sh /opt/lookuply/backups/backup-2025-11-25.tar.gz
```

---

## Scaling

### Vertical Scaling

Upgrade server resources:
- CPX41 → CPX51 (12 vCPU, 32GB RAM)
- Or dedicated server (AX102: 16 cores, 128GB RAM)

### Horizontal Scaling

Deploy to Kubernetes:

```bash
# Apply Kubernetes configs
kubectl apply -f kubernetes/

# Scale API replicas
kubectl scale deployment search-api --replicas=3

# Scale frontend replicas
kubectl scale deployment frontend --replicas=3
```

---

## Security

### Firewall Rules

```bash
# UFW configuration
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### fail2ban

Protects against brute-force attacks:

```bash
# Check status
sudo fail2ban-client status

# Unban IP
sudo fail2ban-client set sshd unbanip <IP>
```

### SSL/TLS

- **A+ rating** on SSL Labs
- TLS 1.2 and 1.3 only
- Strong cipher suites
- HSTS enabled
- OCSP stapling

---

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs service-name

# Check disk space
df -h

# Check memory
free -h
```

**SSL certificate issues:**
```bash
# Renew manually
sudo certbot renew --force-renewal

# Check certificate
sudo certbot certificates
```

**High memory usage:**
```bash
# Check container stats
docker stats

# Reduce OpenSearch memory
# Edit ES_JAVA_OPTS in docker-compose.yml
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/lookuply/.github/blob/main/CONTRIBUTING.md).

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

## Related Projects

- [lookuply/crawler](https://github.com/lookuply/crawler) - Web crawler
- [lookuply/indexer](https://github.com/lookuply/indexer) - Content indexing
- [lookuply/search-api](https://github.com/lookuply/search-api) - Search API
- [lookuply/frontend](https://github.com/lookuply/frontend) - Web interface

---

## Support

- **Documentation**: [docs.lookuply.info](https://docs.lookuply.info)
- **Status**: [status.lookuply.info](https://status.lookuply.info)
- **Email**: [hello@lookuply.info](mailto:hello@lookuply.info)

---

**Open source infrastructure. Built for privacy. Scales with you.**
