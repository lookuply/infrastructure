"""Celery worker log parser."""
import re
from datetime import datetime
from typing import Optional

from . import BaseParser, LogEntry


class CeleryParser(BaseParser):
    """Parse Celery worker logs.

    Handles both Celery task logs and Python tracebacks/errors.
    """

    # Pattern for celery task logs: [2025-12-11 20:40:00,123: INFO/MainProcess] Task app.tasks.crawl[...] succeeded
    CELERY_PATTERN = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+:\s+(\w+)/[^\]]+\]\s+(.+)'

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse Celery log line."""
        line = line.strip()
        if not line:
            return None

        # Try to parse standard Celery format
        match = re.match(self.CELERY_PATTERN, line)
        if match:
            timestamp_str, level_str, message = match.groups()
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

            level = {
                "INFO": "INFO",
                "WARNING": "WARNING",
                "ERROR": "ERROR",
                "CRITICAL": "CRITICAL",
                "DEBUG": "INFO"
            }.get(level_str.upper(), "INFO")

            return LogEntry(
                timestamp=timestamp,
                service="celery",
                level=level,
                message=message
            )

        # Handle Python tracebacks and errors
        level = "INFO"
        if any(keyword in line for keyword in ["Error:", "Exception:", "Traceback", "raise "]):
            level = "ERROR"
        elif any(keyword in line.lower() for keyword in ["warning", "warn"]):
            level = "WARNING"

        # For tracebacks, extract the meaningful part
        message = line
        if "Error:" in line or "Exception:" in line:
            # Extract just the error type and message
            error_match = re.search(r'(\w+(?:Error|Exception)):\s*(.+)', line)
            if error_match:
                error_type, error_msg = error_match.groups()
                message = f"{error_type}: {error_msg}"

        return LogEntry(
            timestamp=datetime.now(),
            service="celery",
            level=level,
            message=message
        )
