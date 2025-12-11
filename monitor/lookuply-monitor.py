#!/usr/bin/env python3
"""Lookuply Log Monitoring Dashboard."""
import signal
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Dict

import yaml
from rich.live import Live

from dashboard import Dashboard
from parsers import BaseParser
from parsers.uvicorn import UvicornParser
from parsers.gin import GinParser
from parsers.crawler import CrawlerParser
from parsers.celery import CeleryParser
from parsers.nginx import NginxAccessParser, NginxErrorParser


class LogMonitor:
    """Monitor Docker logs and log files, update dashboard."""

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
            "coordinator": UvicornParser(),
            "search_api": UvicornParser(),
            "celery": CeleryParser(),
            "crawler": CrawlerParser(),
            "ai_evaluator": GinParser(),
            "nginx_access": NginxAccessParser(),
            "nginx_error": NginxErrorParser(),
        }

        # Track file positions for file-based logs
        self.file_positions: Dict[str, int] = {}
        self.running = True
        self.docker_processes = []

    def follow_docker_logs(self, container_name: str, service: str):
        """Follow Docker logs for a container using subprocess."""
        try:
            # Start docker logs -f process
            process = subprocess.Popen(
                ['docker', 'logs', '-f', '--tail', '0', container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.docker_processes.append(process)

            # Read lines from docker logs
            for line in process.stdout:
                if not self.running:
                    break

                if line.strip():
                    # Parse line
                    parser = self.parsers.get(service)
                    if parser:
                        entry = parser.parse(line)
                        if entry:
                            self.dashboard.add_log(entry)

        except FileNotFoundError:
            print(f"Error: 'docker' command not found. Is Docker installed?", file=sys.stderr)
        except subprocess.SubprocessError as e:
            print(f"Error following Docker logs for {container_name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error with {container_name}: {e}", file=sys.stderr)

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

        except (FileNotFoundError, PermissionError):
            # File might not exist yet or no permission
            pass
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    def monitor_files_loop(self):
        """Main monitoring loop for file-based logs."""
        log_files = self.config.get("log_files", {})

        while self.running:
            # Tail all configured log files
            for service, file_path in log_files.items():
                self.tail_file(file_path, service)

            # Sleep briefly
            time.sleep(0.5)

    def start_docker_monitoring(self):
        """Start monitoring Docker containers."""
        docker_containers = self.config.get("docker_containers", {})

        for service, container_name in docker_containers.items():
            thread = Thread(
                target=self.follow_docker_logs,
                args=(container_name, service),
                daemon=True,
                name=f"docker-{service}"
            )
            thread.start()

    def cleanup(self):
        """Cleanup resources."""
        self.running = False

        # Terminate docker logs processes
        for process in self.docker_processes:
            try:
                process.terminate()
                process.wait(timeout=2)
            except Exception:
                process.kill()

    def run(self):
        """Run the monitoring dashboard."""
        # Start Docker logs monitoring
        self.start_docker_monitoring()

        # Start file monitoring thread
        file_monitor_thread = Thread(target=self.monitor_files_loop, daemon=True)
        file_monitor_thread.start()

        # Setup signal handler
        def signal_handler(sig, frame):
            self.cleanup()
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
            self.cleanup()


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
