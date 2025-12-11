"""Base parser classes for log parsing."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LogEntry:
    """Parsed log entry."""
    timestamp: datetime
    service: str
    level: str  # INFO, WARNING, ERROR, CRITICAL
    message: str
    extra: Optional[dict] = field(default_factory=dict)


class BaseParser(ABC):
    """Abstract base class for log parsers."""

    @abstractmethod
    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse a log line and return a LogEntry if successful."""
        pass
