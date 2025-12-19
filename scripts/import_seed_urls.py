#!/usr/bin/env python3
"""Import seed URLs via Coordinator API."""

import os
import sys
import requests
from typing import List


def import_urls(filename: str, coordinator_url: str = None) -> dict:
    """Import URLs from file via coordinator API.

    Args:
        filename: Path to file with URLs (one per line)
        coordinator_url: Coordinator API URL (default: from env or localhost)

    Returns:
        Dict with added, skipped, total counts
    """
    # Get coordinator URL
    if coordinator_url is None:
        coordinator_url = os.getenv("COORDINATOR_URL", "http://localhost:8001")

    api_url = f"{coordinator_url}/api/v1/urls/batch"

    # Read URLs from file
    print(f"📥 Reading URLs from {filename}...")
    try:
        with open(filename, "r") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)

    if not urls:
        print(f"⚠️  No URLs found in {filename}")
        return {"added": 0, "skipped": 0, "total": 0}

    print(f"   Found {len(urls)} URLs")

    # Prepare batch data - seed URLs get high priority (80)
    batch_data = {
        "urls": [
            {
                "url": url,
                "priority": 80,  # High priority for seed URLs (0-100 scale)
            }
            for url in urls
        ]
    }

    # Send batch import request
    print(f"📤 Importing to coordinator at {coordinator_url}...")
    try:
        response = requests.post(
            api_url,
            json=batch_data,
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        print(f"✅ Import complete!")
        print(f"   Added: {result.get('added', 0)}")
        print(f"   Skipped (duplicates): {result.get('skipped', 0)}")
        print(f"   Total: {result.get('total', 0)}")

        return result

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to coordinator at {coordinator_url}")
        print(f"   Make sure the coordinator is running")
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        print(f"   Response: {e.response.text if e.response else 'N/A'}")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python import_seed_urls.py <urls_file> [coordinator_url]")
        print("\nExample:")
        print("  python import_seed_urls.py seed_urls_wikipedia.txt")
        print("  python import_seed_urls.py seed_urls.txt http://coordinator:8000")
        sys.exit(1)

    filename = sys.argv[1]
    coordinator_url = sys.argv[2] if len(sys.argv) > 2 else None

    import_urls(filename, coordinator_url)


if __name__ == "__main__":
    main()
