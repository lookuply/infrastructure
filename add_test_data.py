#!/usr/bin/env python3
"""Add test data to Meilisearch for demo purposes."""

import os
import requests

# Get Meilisearch credentials from environment
MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_KEY = os.getenv("MEILI_MASTER_KEY")

if not MEILI_KEY:
    print("Error: MEILI_MASTER_KEY environment variable not set")
    exit(1)

# Test documents to index
test_documents = [
    {
        "id": "1",
        "url": "https://en.wikipedia.org/wiki/Slovakia",
        "title": "Slovakia - Wikipedia",
        "content": """Slovakia, officially the Slovak Republic, is a landlocked country in Central Europe.
        It is bordered by Poland to the north, Ukraine to the east, Hungary to the south, Austria to the west,
        and the Czech Republic to the northwest. Slovakia's mostly mountainous territory spans about 49,000 square kilometers,
        hosting a population of over 5.4 million. The capital and largest city is Bratislava, while the second largest city is Košice.
        The official language is Slovak, a member of the Slavic language family.""",
        "language": "en",
        "indexed_at": "2025-12-11T21:00:00Z"
    },
    {
        "id": "2",
        "url": "https://www.slovakia.travel/",
        "title": "Slovakia Travel - Official Tourism Website",
        "content": """Discover Slovakia - a beautiful country in the heart of Europe with stunning mountains,
        medieval castles, and rich cultural heritage. Visit Bratislava Castle, explore the High Tatras mountains,
        or relax in one of many thermal spas. Slovakia offers unique experiences for every traveler.""",
        "language": "en",
        "indexed_at": "2025-12-11T21:00:00Z"
    },
    {
        "id": "3",
        "url": "https://en.wikipedia.org/wiki/Bratislava",
        "title": "Bratislava - Capital of Slovakia",
        "content": """Bratislava is the capital and largest city of Slovakia. Situated in southwestern Slovakia,
        the city straddles the Danube River and is bordered by Austria and Hungary. With a population of about 440,000,
        Bratislava is Slovakia's political, cultural, and economic center. The city features medieval Old Town,
        Bratislava Castle overlooking the Danube, and modern architecture.""",
        "language": "en",
        "indexed_at": "2025-12-11T21:00:00Z"
    },
    {
        "id": "4",
        "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "title": "Python Programming Language - Wikipedia",
        "content": """Python is a high-level, general-purpose programming language. Its design philosophy emphasizes
        code readability with the use of significant indentation. Python is dynamically typed and garbage-collected.
        It supports multiple programming paradigms, including structured, object-oriented and functional programming.
        Python was created by Guido van Rossum and first released in 1991.""",
        "language": "en",
        "indexed_at": "2025-12-11T21:00:00Z"
    },
    {
        "id": "5",
        "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "title": "Artificial Intelligence - Wikipedia",
        "content": """Artificial intelligence (AI) is the simulation of human intelligence processes by machines,
        especially computer systems. Applications of AI include expert systems, natural language processing,
        speech recognition and machine vision. AI research has been highly successful in developing effective
        techniques for solving a wide range of problems, from game playing to medical diagnosis.""",
        "language": "en",
        "indexed_at": "2025-12-11T21:00:00Z"
    }
]

def main():
    """Add test documents to Meilisearch."""
    headers = {
        "Authorization": f"Bearer {MEILI_KEY}",
        "Content-Type": "application/json"
    }

    # Create or update pages index
    print(f"Adding {len(test_documents)} test documents to Meilisearch...")

    response = requests.post(
        f"{MEILI_URL}/indexes/pages/documents",
        headers=headers,
        json=test_documents
    )

    if response.status_code in [200, 202]:
        result = response.json()
        print(f"✅ Successfully queued indexing task: {result.get('taskUid')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Index: pages")
        print(f"   Documents: {len(test_documents)}")
    else:
        print(f"❌ Failed to add documents: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)

    # Configure searchable attributes
    print("\nConfiguring searchable attributes...")
    response = requests.patch(
        f"{MEILI_URL}/indexes/pages/settings/searchable-attributes",
        headers=headers,
        json=["title", "content", "url"]
    )

    if response.status_code == 202:
        print("✅ Searchable attributes configured")
    else:
        print(f"⚠️  Warning: Could not configure searchable attributes: {response.status_code}")

    print("\n🎉 Test data added successfully!")
    print("   Try searching for: Slovakia, Bratislava, Python, AI")

if __name__ == "__main__":
    main()
