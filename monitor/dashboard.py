"""Real-time dashboard using Rich TUI."""
from collections import Counter, deque
from datetime import datetime
from typing import Dict, List

import psutil
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from parsers import LogEntry


class Dashboard:
    """Real-time monitoring dashboard."""

    def __init__(self, max_errors: int = 10, max_logs: int = 5):
        """Initialize dashboard."""
        self.console = Console()
        self.errors = deque(maxlen=max_errors)
        self.logs = deque(maxlen=max_logs)
        self.request_stats = Counter()
        self.service_status: Dict[str, str] = {}
        self.max_errors = max_errors
        self.max_logs = max_logs

    def add_log(self, entry: LogEntry):
        """Add a log entry to the dashboard."""
        # Add to live stream
        self.logs.append(entry)

        # Track errors
        if entry.level in ("ERROR", "CRITICAL"):
            self.errors.append(entry)

        # Update service status
        self.service_status[entry.service] = "healthy"

        # Track request stats
        if entry.extra and "path" in entry.extra:
            self.request_stats[entry.extra["path"]] += 1

    def create_layout(self) -> Layout:
        """Create the dashboard layout."""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=1)
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        layout["left"].split_column(
            Layout(name="status"),
            Layout(name="requests")
        )

        layout["right"].split_column(
            Layout(name="errors"),
            Layout(name="resources")
        )

        return layout

    def render_status(self) -> Panel:
        """Render service status panel."""
        table = Table.grid(padding=1)
        table.add_column(justify="left", style="bold")
        table.add_column(justify="center")

        services = ["coordinator", "search_api", "celery", "nginx"]
        for service in services:
            status = self.service_status.get(service, "unknown")
            icon = "✅" if status == "healthy" else "🔴"
            display_name = service.replace("_", " ").title()
            table.add_row(f"{display_name}:", icon)

        return Panel(table, title="📊 System Status", border_style="blue")

    def render_errors(self) -> Panel:
        """Render errors panel."""
        if not self.errors:
            return Panel(
                Text("No errors", style="dim italic", justify="center"),
                title="🔴 Errors (Last 10)",
                border_style="red"
            )

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Time", style="dim", width=8)
        table.add_column("Service", style="cyan", width=12)
        table.add_column("Message", style="red")

        for error in list(self.errors)[::-1]:  # Show most recent first
            table.add_row(
                error.timestamp.strftime("%H:%M:%S"),
                f"[{error.service}]",
                error.message[:40] + "..." if len(error.message) > 40 else error.message
            )

        return Panel(table, title="🔴 Errors (Last 10)", border_style="red")

    def render_requests(self) -> Panel:
        """Render request statistics panel."""
        if not self.request_stats:
            return Panel(
                Text("No requests yet", style="dim italic", justify="center"),
                title="📈 Request Stats",
                border_style="green"
            )

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Endpoint", style="bold")
        table.add_column("Count", justify="right", style="cyan")

        total = sum(self.request_stats.values())
        table.add_row("Total:", str(total), style="bold green")
        table.add_row("", "")  # Spacer

        # Top 5 endpoints
        for path, count in self.request_stats.most_common(5):
            table.add_row(path[:30], str(count))

        return Panel(table, title="📈 Request Stats", border_style="green")

    def render_resources(self) -> Panel:
        """Render resource usage panel."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Create progress bars
        progress = Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=15),
            TextColumn("[bold]{task.percentage:>3.0f}%"),
            expand=False
        )

        cpu_task = progress.add_task("CPU ", total=100, completed=cpu_percent)
        mem_task = progress.add_task("RAM ", total=100, completed=memory.percent)
        disk_task = progress.add_task("Disk", total=100, completed=disk.percent)

        # Add text info
        text = Text()
        text.append(f"\n RAM:  {memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB\n", style="dim")
        text.append(f" Disk: {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB", style="dim")

        from rich.columns import Columns
        content = Columns([progress, text], expand=False, padding=(0, 2))

        return Panel(content, title="💾 Resource Usage", border_style="yellow")

    def render_logs(self) -> Panel:
        """Render live log stream panel."""
        if not self.logs:
            return Panel(
                Text("Waiting for logs...", style="dim italic", justify="center"),
                title="📜 Live Log Stream (last 5)",
                border_style="magenta"
            )

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Time", style="dim", width=8)
        table.add_column("Service", style="cyan", width=12)
        table.add_column("Message")

        for log in list(self.logs)[::-1]:  # Show most recent first
            level_style = {
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red"
            }.get(log.level, "white")

            table.add_row(
                log.timestamp.strftime("%H:%M:%S"),
                f"[{log.service}]",
                Text(log.message[:50] + "..." if len(log.message) > 50 else log.message, style=level_style)
            )

        return Panel(table, title="📜 Live Log Stream (last 5)", border_style="magenta")

    def render(self) -> Layout:
        """Render the complete dashboard."""
        layout = self.create_layout()

        # Header
        header_text = Text("LOOKUPLY MONITORING DASHBOARD", style="bold magenta", justify="center")
        layout["header"].update(Panel(header_text, border_style="bright_magenta"))

        # Panels
        layout["status"].update(self.render_status())
        layout["requests"].update(self.render_requests())
        layout["errors"].update(self.render_errors())
        layout["resources"].update(self.render_resources())

        # Footer
        footer_text = Text("Press Ctrl+C to quit | Refreshing every 1s", style="dim", justify="center")
        layout["footer"].update(Panel(footer_text, border_style="dim"))

        # Replace one panel with logs
        layout["main"].split_column(
            Layout(name="top"),
            Layout(name="logs", size=10)
        )
        layout["top"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        layout["left"].split_column(
            Layout(name="status"),
            Layout(name="requests")
        )
        layout["right"].split_column(
            Layout(name="errors"),
            Layout(name="resources")
        )

        layout["status"].update(self.render_status())
        layout["requests"].update(self.render_requests())
        layout["errors"].update(self.render_errors())
        layout["resources"].update(self.render_resources())
        layout["logs"].update(self.render_logs())

        return layout
