"""Gin (Go web framework) log parser."""
import re
from datetime import datetime
from typing import Optional

from . import BaseParser, LogEntry


class GinParser(BaseParser):
    """Parse Gin/Go web framework logs.

    Format: [GIN] 2025/12/11 - 20:36:00 | 200 |     294.081µs |             ::1 | GET      "/api/tags"
    """

    # Pattern: [GIN] DATE - TIME | STATUS | DURATION | IP | METHOD PATH
    PATTERN = r'\[GIN\]\s+(\d{4}/\d{2}/\d{2})\s+-\s+(\d{2}:\d{2}:\d{2})\s+\|\s+(\d+)\s+\|[^|]+\|[^|]+\|\s+(\w+)\s+"([^"]+)"'

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse Gin log line."""
        match = re.search(self.PATTERN, line.strip())
        if not match:
            return None

        date_str, time_str, status, method, path = match.groups()

        # Parse timestamp
        timestamp_str = f"{date_str} {time_str}"
        timestamp = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")

        # Determine level from status code
        status_int = int(status)
        if status_int >= 500:
            level = "ERROR"
        elif status_int >= 400:
            level = "WARNING"
        else:
            level = "INFO"

        message = f"{method} {path} → {status}"

        return LogEntry(
            timestamp=timestamp,
            service="ai_evaluator",  # Will be overridden by monitor
            level=level,
            message=message,
            extra={"method": method, "path": path, "status": status_int}
        )
