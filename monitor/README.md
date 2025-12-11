# Lookuply Log Monitor

Real-time console dashboard for monitoring Lookuply service logs.

## Features

- 📊 Service status tracking
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

- Log file paths
- Dashboard refresh rate
- Alert thresholds
- Maximum errors/logs to display

## Requirements

- Python 3.13+
- Read access to log files (may require sudo)
- Terminal with Unicode support

## Logs Monitored

- **Coordinator**: URL frontier and task queue
- **Search API**: Search queries and LLM requests
- **Celery Worker**: Background task processing
- **Nginx**: HTTP access and error logs

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│              LOOKUPLY MONITORING DASHBOARD              │
├─────────────────────────────────────────────────────────┤
│  📊 System Status        🔴 Errors (Last 10)           │
│  📈 Request Stats        💾 Resource Usage             │
│  📜 Live Log Stream (last 5)                           │
└─────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

- **Ctrl+C**: Quit the monitor

## Troubleshooting

### Permission Denied

If you see permission errors, run with sudo:

```bash
sudo ./run.sh
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
