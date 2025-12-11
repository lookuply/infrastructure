"""Nginx log parser."""
import re
from datetime import datetime
from typing import Optional

from . import BaseParser, LogEntry


class NginxAccessParser(BaseParser):
    """Parser for nginx access logs."""

    # Nginx access log format:
    # 127.0.0.1 - - [10/Dec/2025:10:30:45 +0000] "GET /api/chat HTTP/1.1" 200 ...

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse an nginx access log line."""
        # Extract method, path, status
        match = re.search(r'"(\w+) ([^ ]+) HTTP/[\d.]+" (\d{3})', line)
        if not match:
            return None

        method, path, status = match.groups()

        # Determine log level based on status code
        status_int = int(status)
        if status_int >= 500:
            level = "ERROR"
        elif status_int >= 400:
            level = "WARNING"
        else:
            level = "INFO"

        return LogEntry(
            timestamp=datetime.now(),  # Simplified - could parse nginx timestamp
            service="nginx",
            level=level,
            message=f"{method} {path} → {status}",
            extra={"method": method, "path": path, "status": status_int}
        )


class NginxErrorParser(BaseParser):
    """Parser for nginx error logs."""

    # 2025/12/10 10:30:45 [error] 123#123: *456 ...
    PATTERN = r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] .+?: (.+)"

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse an nginx error log line."""
        match = re.match(self.PATTERN, line.strip())
        if not match:
            return None

        timestamp_str, level, message = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None

        return LogEntry(
            timestamp=timestamp,
            service="nginx",
            level=level.upper(),
            message=message
        )
