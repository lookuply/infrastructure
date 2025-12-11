"""Coordinator log parser."""
import re
from datetime import datetime
from typing import Optional

from . import BaseParser, LogEntry


class CoordinatorParser(BaseParser):
    """Parser for coordinator service logs."""

    # Pattern: 2025-12-10 10:30:45 - INFO - Message
    PATTERN = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)"

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse a coordinator log line."""
        match = re.match(self.PATTERN, line.strip())
        if not match:
            return None

        timestamp_str, level, message = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

        return LogEntry(
            timestamp=timestamp,
            service="coordinator",
            level=level,
            message=message
        )
