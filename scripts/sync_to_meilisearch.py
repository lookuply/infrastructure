#!/usr/bin/env python3
"""Sync evaluated pages to Meilisearch via Coordinator API."""

import os
import sys
import requests
from typing import List, Dict


def fetch_evaluated_pages(coordinator_url: str, limit: int = 100, offset: int = 0) -> List[Dict]:
    """Fetch evaluated pages from coordinator API.

    Args:
        coordinator_url: Coordinator API URL
        limit: Number of pages to fetch per request
        offset: Offset for pagination

    Returns:
        List of page dicts
    """
    api_url = f"{coordinator_url}/api/v1/pages"
    params = {
        'status': 'evaluated',
        'limit': limit,
        'offset': offset
    }

    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('pages', [])
    except Exception as e:
        print(f"❌ Error fetching pages: {e}")
        return []


def index_to_meilisearch(pages: List[Dict], meilisearch_url: str, api_key: str = None) -> int:
    """Index pages to Meilisearch.

    Args:
        pages: List of page dicts
        meilisearch_url: Meilisearch server URL
        api_key: Optional Meilisearch API key

    Returns:
        Number of pages indexed
    """
    if not pages:
        return 0

    # Prepare documents for indexing
    documents = []
    for page in pages:
        doc = {
            'id': page.get('id'),
            'url': page.get('url'),
            'title': page.get('title', ''),
            'content': page.get('content', ''),
            'summary': page.get('summary', ''),
            'language': page.get('language', 'en'),
            'ai_score': page.get('ai_score', 0),
            'depth': page.get('depth', 0),
            'evaluated_at': page.get('evaluated_at')
        }
        documents.append(doc)

    # Index to Meilisearch
    index_url = f"{meilisearch_url}/indexes/pages/documents"
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    try:
        response = requests.post(
            index_url,
            json=documents,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        return len(documents)
    except Exception as e:
        print(f"❌ Error indexing to Meilisearch: {e}")
        return 0


def sync(coordinator_url: str, meilisearch_url: str, meilisearch_key: str = None):
    """Sync all evaluated pages to Meilisearch.

    Args:
        coordinator_url: Coordinator API URL
        meilisearch_url: Meilisearch server URL
        meilisearch_key: Optional Meilisearch API key
    """
    print("🔄 Lookuply → Meilisearch Sync")
    print("=" * 60)
    print(f"Coordinator: {coordinator_url}")
    print(f"Meilisearch: {meilisearch_url}")
    print()

    total_indexed = 0
    offset = 0
    limit = 100

    while True:
        print(f"📥 Fetching pages (offset={offset}, limit={limit})...")
        pages = fetch_evaluated_pages(coordinator_url, limit=limit, offset=offset)

        if not pages:
            print("   No more pages to fetch")
            break

        print(f"   Fetched {len(pages)} pages")

        print(f"📤 Indexing to Meilisearch...")
        indexed = index_to_meilisearch(pages, meilisearch_url, meilisearch_key)
        total_indexed += indexed
        print(f"   ✅ Indexed {indexed} pages")

        # Next batch
        offset += limit

        # If we got fewer pages than limit, we're done
        if len(pages) < limit:
            break

    print()
    print("=" * 60)
    print(f"✅ Sync complete! Total indexed: {total_indexed} pages")


def main():
    """CLI entry point."""
    # Get configuration from environment or defaults
    coordinator_url = os.getenv("COORDINATOR_URL", "http://localhost:8001")
    meilisearch_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meilisearch_key = os.getenv("MEILISEARCH_MASTER_KEY")

    # Allow CLI overrides
    if len(sys.argv) > 1:
        coordinator_url = sys.argv[1]
    if len(sys.argv) > 2:
        meilisearch_url = sys.argv[2]

    sync(coordinator_url, meilisearch_url, meilisearch_key)


if __name__ == "__main__":
    main()
