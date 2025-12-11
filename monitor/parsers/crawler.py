"""Crawler node log parser."""
import re
from datetime import datetime
from typing import Optional

from . import BaseParser, LogEntry


class CrawlerParser(BaseParser):
    """Parse crawler node logs.

    Format examples:
    - Discovered 31 links from https://...: 7 new, 24 duplicates
    - Crawling URL: https://...
    - Error: ...
    """

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse crawler log line."""
        line = line.strip()
        if not line:
            return None

        # Determine level and extract message
        level = "INFO"
        message = line

        # Check for error patterns
        if any(keyword in line.lower() for keyword in ["error", "exception", "failed", "traceback"]):
            level = "ERROR"
        elif any(keyword in line.lower() for keyword in ["warning", "warn"]):
            level = "WARNING"

        # Extract structured info for specific patterns
        extra = {}

        # Pattern: Discovered N links from URL: X new, Y duplicates
        discovered_match = re.search(r'Discovered (\d+) links from ([^:]+): (\d+) new, (\d+) duplicates', line)
        if discovered_match:
            total, url, new, dupes = discovered_match.groups()
            extra = {
                "total_links": int(total),
                "new_links": int(new),
                "duplicate_links": int(dupes),
                "source_url": url
            }
            message = f"Discovered {new} new links from {url[:50]}..."

        return LogEntry(
            timestamp=datetime.now(),
            service="crawler",
            level=level,
            message=message,
            extra=extra if extra else None
        )
