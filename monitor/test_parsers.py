#!/usr/bin/env python3
"""Quick test to verify parsers work with real log formats."""

from parsers.uvicorn import UvicornParser
from parsers.gin import GinParser
from parsers.crawler import CrawlerParser
from parsers.celery import CeleryParser
from parsers.nginx import NginxAccessParser


def test_parsers():
    """Test each parser with sample log lines."""

    # Test UvicornParser
    print("Testing UvicornParser...")
    uvicorn_parser = UvicornParser()
    test_lines = [
        'INFO:     172.18.0.7:35800 - "POST /api/v1/urls/159356/crawling HTTP/1.1" 200 OK',
        'INFO:     127.0.0.1:54784 - "GET /health HTTP/1.1" 200 OK',
    ]
    for line in test_lines:
        result = uvicorn_parser.parse(line)
        if result:
            print(f"  ✅ Parsed: {result.level} - {result.message}")
        else:
            print(f"  ❌ Failed to parse: {line[:50]}")

    # Test GinParser
    print("\nTesting GinParser...")
    gin_parser = GinParser()
    test_lines = [
        '[GIN] 2025/12/11 - 20:36:00 | 200 |     294.081µs |             ::1 | GET      "/api/tags"',
    ]
    for line in test_lines:
        result = gin_parser.parse(line)
        if result:
            print(f"  ✅ Parsed: {result.level} - {result.message}")
        else:
            print(f"  ❌ Failed to parse: {line[:50]}")

    # Test CrawlerParser
    print("\nTesting CrawlerParser...")
    crawler_parser = CrawlerParser()
    test_lines = [
        'Discovered 31 links from https://example.com: 7 new, 24 duplicates',
    ]
    for line in test_lines:
        result = crawler_parser.parse(line)
        if result:
            print(f"  ✅ Parsed: {result.level} - {result.message}")
        else:
            print(f"  ❌ Failed to parse: {line[:50]}")

    # Test CeleryParser
    print("\nTesting CeleryParser...")
    celery_parser = CeleryParser()
    test_lines = [
        'ModuleNotFoundError: No module named \'app\'',
    ]
    for line in test_lines:
        result = celery_parser.parse(line)
        if result:
            print(f"  ✅ Parsed: {result.level} - {result.message}")
        else:
            print(f"  ❌ Failed to parse: {line[:50]}")

    print("\n✅ All parsers tested!")


if __name__ == "__main__":
    test_parsers()
