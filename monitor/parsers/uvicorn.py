"""Uvicorn/FastAPI log parser."""
import re
from datetime import datetime
from typing import Optional

from . import BaseParser, LogEntry


class UvicornParser(BaseParser):
    """Parse uvicorn/FastAPI logs.

    Format: INFO:     172.18.0.7:35800 - "POST /api/v1/urls/159356/crawling HTTP/1.1" 200 OK
    """

    # Pattern: LEVEL:     IP:PORT - "METHOD PATH HTTP/VERSION" STATUS MESSAGE
    PATTERN = r'(\w+):\s+([^\s]+)\s+-\s+"(\w+)\s+([^\s]+)\s+HTTP/[\d.]+"\s+(\d+)'

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse uvicorn log line."""
        match = re.search(self.PATTERN, line.strip())
        if not match:
            return None

        level_str, client, method, path, status = match.groups()

        # Map uvicorn levels to standard levels
        level = {
            "INFO": "INFO",
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL",
            "DEBUG": "INFO"
        }.get(level_str.upper(), "INFO")

        # Determine level from status code if INFO
        if level == "INFO":
            status_int = int(status)
            if status_int >= 500:
                level = "ERROR"
            elif status_int >= 400:
                level = "WARNING"

        message = f"{method} {path} → {status}"

        return LogEntry(
            timestamp=datetime.now(),
            service="api",  # Will be overridden by monitor
            level=level,
            message=message,
            extra={"method": method, "path": path, "status": int(status), "client": client}
        )
