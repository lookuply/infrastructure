#!/usr/bin/env python3
"""Lookuply Log Monitoring Dashboard."""
import signal
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Dict, List

import yaml
from rich.live import Live

from dashboard import Dashboard
from parsers import BaseParser
from parsers.coordinator import CoordinatorParser
from parsers.nginx import NginxAccessParser, NginxErrorParser


class LogMonitor:
    """Monitor log files and update dashboard."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize monitor."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize dashboard
        dashboard_config = self.config.get("dashboard", {})
        self.dashboard = Dashboard(
            max_errors=dashboard_config.get("max_errors", 10),
            max_logs=dashboard_config.get("max_logs", 5)
        )

        # Initialize parsers
        self.parsers: Dict[str, BaseParser] = {
            "coordinator": CoordinatorParser(),
            "search_api": CoordinatorParser(),  # Same format
            "celery": CoordinatorParser(),  # Same format
            "nginx_access": NginxAccessParser(),
            "nginx_error": NginxErrorParser(),
        }

        # Track file positions
        self.file_positions: Dict[str, int] = {}
        self.running = True

    def tail_file(self, file_path: str, service: str):
        """Tail a log file and parse new lines."""
        path = Path(file_path)

        # Initialize file position
        if file_path not in self.file_positions:
            try:
                self.file_positions[file_path] = path.stat().st_size if path.exists() else 0
            except (FileNotFoundError, PermissionError):
                return

        try:
            with open(file_path, 'r') as f:
                # Seek to last position
                f.seek(self.file_positions[file_path])

                # Read new lines
                while line := f.readline():
                    if line.strip():
                        # Parse line
                        parser = self.parsers.get(service)
                        if parser:
                            entry = parser.parse(line)
                            if entry:
                                self.dashboard.add_log(entry)

                # Update position
                self.file_positions[file_path] = f.tell()

        except (FileNotFoundError, PermissionError) as e:
            # File might not exist yet or no permission
            pass
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    def monitor_loop(self):
        """Main monitoring loop."""
        log_config = self.config.get("logs", {})

        while self.running:
            # Tail all configured log files
            for service, file_path in log_config.items():
                self.tail_file(file_path, service)

            # Sleep briefly
            time.sleep(0.5)

    def run(self):
        """Run the monitoring dashboard."""
        # Start monitoring thread
        monitor_thread = Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()

        # Setup signal handler
        def signal_handler(sig, frame):
            self.running = False
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run dashboard
        try:
            with Live(self.dashboard.render(), refresh_per_second=1, screen=True) as live:
                while self.running:
                    live.update(self.dashboard.render())
                    time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config.yaml"

    # Check if config exists
    if not Path(config_path).exists():
        print(f"Error: Configuration file '{config_path}' not found.", file=sys.stderr)
        print("Usage: python lookuply-monitor.py [config.yaml]", file=sys.stderr)
        sys.exit(1)

    monitor = LogMonitor(config_path)
    monitor.run()


if __name__ == "__main__":
    main()
