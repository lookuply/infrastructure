#!/usr/bin/env python3
"""
Generate quality seed URLs for Lookuply crawler
Focus: 24 EU languages, high-quality content
"""

# 24 official EU languages (ISO 639-1 codes)
EU_LANGUAGES = [
    'bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr',
    'ga', 'hr', 'hu', 'it', 'lt', 'lv', 'mt', 'nl', 'pl', 'pt',
    'ro', 'sk', 'sl', 'sv'
]

# Wikipedia top categories for each language
WIKIPEDIA_TOPICS = [
    'Artificial_intelligence',
    'Computer_science',
    'Programming',
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'History',
    'Geography',
    'Philosophy',
    'Technology',
    'Science',
    'Internet',
    'Software',
    'Web_development',
    'Database',
    'Machine_learning',
    'Data_science',
]

# High-quality documentation sites
DOCUMENTATION_SITES = [
    # Programming languages
    'https://docs.python.org/',
    'https://developer.mozilla.org/',  # MDN
    'https://docs.oracle.com/en/java/',
    'https://learn.microsoft.com/',
    'https://doc.rust-lang.org/',
    'https://go.dev/doc/',
    'https://www.php.net/docs.php',
    'https://docs.ruby-lang.org/',

    # Frameworks & Tools
    'https://react.dev/',
    'https://vuejs.org/guide/',
    'https://angular.io/docs',
    'https://nodejs.org/docs/',
    'https://www.postgresql.org/docs/',
    'https://redis.io/docs/',
    'https://docs.docker.com/',
    'https://kubernetes.io/docs/',

    # Standards & References
    'https://www.w3.org/',
    'https://html.spec.whatwg.org/',
    'https://tc39.es/ecma262/',

    # Open source
    'https://www.apache.org/',
    'https://www.gnu.org/',
    'https://www.kernel.org/',
]

# High-quality content sites (multi-language)
QUALITY_SITES = [
    'https://stackoverflow.com/',
    'https://github.com/',
    'https://arxiv.org/',
    'https://www.nature.com/',
    'https://www.sciencedirect.com/',
    'https://plato.stanford.edu/',  # Stanford Encyclopedia of Philosophy
    'https://www.britannica.com/',
    'https://www.gutenberg.org/',  # Free books
]

# EU official sites
EU_OFFICIAL_SITES = [
    'https://europa.eu/',
    'https://eur-lex.europa.eu/',  # EU law
    'https://cordis.europa.eu/',  # Research
    'https://ec.europa.eu/',
]


def generate_wikipedia_urls():
    """Generate Wikipedia seed URLs for 24 EU languages"""
    urls = []

    for lang in EU_LANGUAGES:
        # Main page
        urls.append(f'https://{lang}.wikipedia.org/wiki/Main_Page')

        # Top topics
        for topic in WIKIPEDIA_TOPICS[:10]:  # Top 10 topics per language
            urls.append(f'https://{lang}.wikipedia.org/wiki/{topic}')

    return urls


def generate_seed_list():
    """Generate complete seed URL list"""
    print("🌱 Generating Lookuply Seed URLs")
    print("=" * 60)

    urls = []

    # 1. Wikipedia (multi-language)
    print("\n📚 Wikipedia URLs (24 EU languages)...")
    wiki_urls = generate_wikipedia_urls()
    urls.extend(wiki_urls)
    print(f"   Added {len(wiki_urls)} Wikipedia URLs")

    # 2. Documentation sites
    print("\n📖 Documentation sites...")
    urls.extend(DOCUMENTATION_SITES)
    print(f"   Added {len(DOCUMENTATION_SITES)} documentation sites")

    # 3. Quality content sites
    print("\n⭐ Quality content sites...")
    urls.extend(QUALITY_SITES)
    print(f"   Added {len(QUALITY_SITES)} quality sites")

    # 4. EU official sites
    print("\n🇪🇺 EU official sites...")
    urls.extend(EU_OFFICIAL_SITES)
    print(f"   Added {len(EU_OFFICIAL_SITES)} EU sites")

    print("\n" + "=" * 60)
    print(f"✅ Total: {len(urls)} seed URLs")

    return urls


def save_seed_urls(urls, filename='seed_urls.txt'):
    """Save URLs to file"""
    with open(filename, 'w') as f:
        for url in urls:
            f.write(url + '\n')
    print(f"\n💾 Saved to {filename}")


def generate_by_category():
    """Generate categorized seed lists"""
    categories = {
        'wikipedia': generate_wikipedia_urls(),
        'documentation': DOCUMENTATION_SITES,
        'quality_content': QUALITY_SITES,
        'eu_official': EU_OFFICIAL_SITES,
    }

    for category, urls in categories.items():
        filename = f'seed_urls_{category}.txt'
        with open(filename, 'w') as f:
            for url in urls:
                f.write(url + '\n')
        print(f"   ✓ {filename} ({len(urls)} URLs)")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--by-category':
        print("🌱 Generating categorized seed URL lists")
        print("=" * 60)
        generate_by_category()
    else:
        urls = generate_seed_list()
        save_seed_urls(urls)

        print("\n📊 Breakdown by language (Wikipedia):")
        print(f"   Languages: {len(EU_LANGUAGES)}")
        print(f"   Topics per language: ~10")
        print(f"   Total Wikipedia: ~{len(EU_LANGUAGES) * 11} URLs")

        print("\n🚀 To generate by category:")
        print("   python generate_seed_urls.py --by-category")
