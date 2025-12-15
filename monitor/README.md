# Lookuply Log Monitor

Real-time console dashboard for monitoring Lookuply service logs.

## Features

- 📊 Service status tracking
- 🤖 **AI Processing Progress** (NEW) - Real-time AI worker statistics
- 🔴 Error monitoring (last 10 errors)
- 📈 Request statistics
- 💾 Resource usage (CPU, RAM, Disk)
- 📜 Live log stream
- ⚡ Real-time updates

## Installation

```bash
cd /home/baskervil/lookuply/infrastructure/monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
./run.sh
```

### Manual Run

```bash
source venv/bin/activate
python3 lookuply-monitor.py
```

### With Custom Config

```bash
python3 lookuply-monitor.py /path/to/config.yaml
```

## Configuration

Edit `config.yaml` to customize:

**Docker Containers:**
```yaml
docker_containers:
  coordinator: lookuply-coordinator
  search_api: lookuply-search-api
  # Add more containers...
```

**File-Based Logs:**
```yaml
log_files:
  nginx_access: /var/log/nginx/access.log
  nginx_error: /var/log/nginx/error.log
```

**API Endpoints:**
```yaml
api:
  coordinator_url: http://localhost:8000
```

**Dashboard Settings:**
- Refresh rate
- Alert thresholds
- Maximum errors/logs to display

## Requirements

- Python 3.13+
- Read access to log files (may require sudo)
- Terminal with Unicode support

## Logs Monitored

### Docker Containers (via `docker logs`)
- **Coordinator**: URL frontier and task queue (`lookuply-coordinator`)
- **Search API**: Search queries and LLM requests (`lookuply-search-api`)
- **Celery Worker**: Background task processing (`lookuply-celery-worker`)
- **Crawler Node**: Web crawling operations (`lookuply-crawler-node`)
- **AI Evaluator**: LLM page evaluation (`lookuply-ai-evaluator`)

### File-Based Logs
- **Nginx Access**: HTTP requests (`/var/log/nginx/access.log`)
- **Nginx Error**: Server errors (`/var/log/nginx/error.log`)

## Dashboard Layout

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      LOOKUPLY MONITORING DASHBOARD                            │
├───────────────────────────────────────────────────────────────────────────────┤
│  📊 System Status    │  📈 Request Stats      │  🔴 Errors (Last 10)        │
│  🤖 AI Progress      │  💾 Resource Usage     │  📜 Live Log Stream (5)     │
└───────────────────────────────────────────────────────────────────────────────┘
```

### AI Processing Progress Panel

Displays real-time statistics from the coordinator's AI worker pipeline:

- **✅ Evaluated**: Successfully processed pages
- **⏳ Pending**: Pages waiting for processing
- **🔄 Processing**: Pages currently being processed
- **❌ Failed**: Pages that failed processing
- **👷 Workers**: Number of active AI workers
- **📊 Progress Bar**: Visual completion percentage

**Data Source**: Fetches from `GET /coordinator/worker-stats` endpoint every 1 second.

## Keyboard Shortcuts

- **Ctrl+C**: Quit the monitor

## Troubleshooting

### Permission Denied (Nginx logs)

Nginx logs require root access. The script automatically uses sudo if needed.

If you still see permission errors:

```bash
sudo ./run.sh
```

### Docker Command Not Found

Make sure Docker is installed and accessible:

```bash
docker --version
docker ps
```

### No Logs Appearing

Check that log paths in `config.yaml` are correct:

```bash
ls -la /var/lib/docker/volumes/lookuply_coordinator_logs/_data/
ls -la /var/log/nginx/
```

### Dependencies Not Installing

Make sure you're using Python 3.13+:

```bash
python3 --version
```

## Development

### Project Structure

```
monitor/
├── lookuply-monitor.py      # Main script
├── dashboard.py             # Rich TUI dashboard
├── config.yaml              # Configuration
├── requirements.txt         # Dependencies
├── parsers/
│   ├── __init__.py          # Base parser
│   ├── coordinator.py       # Coordinator log parser
│   └── nginx.py             # Nginx log parser
└── run.sh                   # Run script
```

### Adding New Parsers

1. Create a new parser in `parsers/`:
```python
from . import BaseParser, LogEntry

class MyParser(BaseParser):
    def parse(self, line: str) -> Optional[LogEntry]:
        # Parse logic here
        pass
```

2. Add to `lookuply-monitor.py`:
```python
from parsers.my_parser import MyParser

self.parsers["my_service"] = MyParser()
```

3. Update `config.yaml`:
```yaml
logs:
  my_service: /path/to/log.log
```

## License

MIT License - Part of the Lookuply project
