#!/usr/bin/env python3
"""Test UvicornParser with actual logs."""

from parsers.uvicorn import UvicornParser

parser = UvicornParser()

# Test with actual coordinator logs (copied from docker logs output)
test_lines = [
    'INFO:     172.18.0.7:54026 - "POST /api/v1/urls/159780/crawling HTTP/1.1" 200 OK',
    'INFO:     172.18.0.7:55812 - "POST /api/v1/urls/batch HTTP/1.1" 200 OK',
    'INFO:     172.18.0.7:55812 - "POST /api/v1/urls/159778/completed HTTP/1.1" 200 OK',
    'INFO:     127.0.0.1:54784 - "GET /health HTTP/1.1" 200 OK',
]

print("Testing UvicornParser with real coordinator logs:\n")
for line in test_lines:
    result = parser.parse(line)
    if result:
        print(f'✅ MATCH - Level: {result.level}, Message: {result.message}')
    else:
        print(f'❌ NO MATCH - Line: {line[:70]}')
