"""Post analyzer — company extraction, headcount estimation, relevance scoring."""

import json
import re

# Known companies with estimated employee counts in Hungary
KNOWN_COMPANIES = {
    'otp': {'name': 'OTP Bank', 'size': 'large', 'sector': 'fintech'},
    'ericsson': {'name': 'Ericsson', 'size': 'large', 'sector': 'telecom'},
    'nng': {'name': 'NNG', 'size': 'medium', 'sector': 'automotive/nav'},
    'microsoft': {'name': 'Microsoft', 'size': 'large', 'sector': 'big tech'},
    'continental': {'name': 'Continental', 'size': 'large', 'sector': 'automotive'},
    'docler': {'name': 'Docler/Byborg', 'size': 'large', 'sector': 'entertainment'},
    'byborg': {'name': 'Docler/Byborg', 'size': 'large', 'sector': 'entertainment'},
    'szállás': {'name': 'Szállás Group', 'size': 'medium', 'sector': 'travel'},
    'szallas': {'name': 'Szállás Group', 'size': 'medium', 'sector': 'travel'},
    'lensa': {'name': 'Lensa', 'size': 'small', 'sector': 'AI/startup'},
    'seon': {'name': 'SEON', 'size': 'medium', 'sector': 'fintech/startup'},
    'unisys': {'name': 'Unisys', 'size': 'medium', 'sector': 'IT services'},
    'catl': {'name': 'CATL', 'size': 'large', 'sector': 'battery/manufacturing'},
    'audi': {'name': 'Audi', 'size': 'large', 'sector': 'automotive'},
    'mnb': {'name': 'MNB', 'size': 'medium', 'sector': 'finance/gov'},
    'tesco': {'name': 'Tesco Technology', 'size': 'medium', 'sector': 'retail tech'},
    'mol digital': {'name': 'MOL', 'size': 'large', 'sector': 'energy'},
    'mol group': {'name': 'MOL', 'size': 'large', 'sector': 'energy'},
}

# Headcount estimation ranges by company size
HEADCOUNT_RANGES = {
    'large': (50, 200),
    'medium': (20, 80),
    'small': (5, 30),
}

LAYOFF_KEYWORDS = [
    'leépít', 'elbocsát', 'kirúg', 'létszámcsökk', 'layoff', 'fired',
    'let go', 'megszün', 'bezár', 'leépülés',
]

STRONG_SIGNAL_KEYWORDS = [
    'álláspiac', 'hiring freeze', 'nem vesznek fel', 'bújtatott',
    'quiet firing', 'quiet quitting', 'felvételi stop', 'nincs felvétel',
    'nem talál munkát', 'nincs munka', 'álláskeres',
]

ANXIETY_KEYWORDS = [
    'megéri tanulni', 'merre tovább', 'exit terv', 'váltanátok',
    'elbizonytalanodtam', 'kiégés', 'imposztor', 'süllyedő hajó',
]

AI_KEYWORDS_CONTEXT = [
    # These need to appear near layoff/job keywords to count
    'mesterséges intelligencia', 'gépi tanulás', 'machine learning',
    'chatgpt', 'copilot', 'github copilot', 'claude',
    'ai elveszi', 'ai miatt', 'ai-val helyettesít', 'ai váltja ki',
    'automatizál', 'llm',
]

AI_KEYWORDS_STRONG = [
    # These are strong enough on their own (explicitly about AI replacing jobs)
    'ai elveszi a munkát', 'ai elveszi a munkánkat',
    'ai miatt leépít', 'ai miatt elbocsát',
    'ai helyettesít', 'mesterséges intelligencia elveszi',
]

FREEZE_KEYWORDS = [
    'hiring freeze', 'felvételi stop', 'nem vesznek fel',
    'nincs nyitott pozíció', 'álláspiac beszűkült', 'nincs felvétel',
    'nehéz elhelyezkedni', 'nem talál munkát', 'álláspiac roml',
]


def _extract_company(post):
    """Extract company name from post title, selftext, and comments."""
    title = post.get('title', '').lower()
    selftext = post.get('selftext', '').lower()
    comments_text = ' '.join(
        c.get('body', '').lower() for c in post.get('top_comments', [])
    )

    # Check title first (strongest signal)
    for key, info in KNOWN_COMPANIES.items():
        # Use word boundary for short keys to avoid false positives
        if len(key) <= 4:
            if re.search(r'\b' + re.escape(key) + r'\b', title, re.IGNORECASE):
                return info['name'], 'title', info['size'], info['sector']
        elif key in title:
            return info['name'], 'title', info['size'], info['sector']

    # Check selftext
    for key, info in KNOWN_COMPANIES.items():
        if len(key) <= 4:
            if re.search(r'\b' + re.escape(key) + r'\b', selftext, re.IGNORECASE):
                return info['name'], 'selftext', info['size'], info['sector']
        elif key in selftext:
            return info['name'], 'selftext', info['size'], info['sector']

    # Check comments
    for key, info in KNOWN_COMPANIES.items():
        if len(key) <= 4:
            if re.search(r'\b' + re.escape(key) + r'\b', comments_text, re.IGNORECASE):
                return info['name'], 'comment', info['size'], info['sector']
        elif key in comments_text:
            return info['name'], 'comment', info['size'], info['sector']

    return None, 'none', None, None


def _extract_headcount(post):
    """Extract or estimate headcount from post content."""
    title = post.get('title', '')
    selftext = post.get('selftext', '')
    text = f'{title} {selftext}'

    # Try to find explicit numbers near layoff keywords
    patterns = [
        r'(\d+)\s*(?:embert?|főt?|kolléga|dolgozó|fejlesztő|munkavállal)',
        r'(?:kb|körülbelül|mintegy|nagyjából)\s*(\d+)',
        r'(\d+)\s*(?:fős|fővel)\s*(?:leépítés|elbocsát)',
        r'(\d+)%',  # percentage — we'll handle differently
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num > 0 and num < 10000:  # sanity check
                return num, num, 'explicit'

    return None, None, None


def _estimate_headcount(company_size, post):
    """Heuristic headcount estimation when no explicit number found."""
    if not company_size:
        # Try to guess from context
        text = (post.get('title', '') + ' ' + post.get('selftext', '')).lower()
        if any(w in text for w in ['multi', 'nagyvállalat', 'nagy cég']):
            company_size = 'large'
        elif any(w in text for w in ['startup', 'kis cég', 'kkv']):
            company_size = 'small'
        else:
            return None, None, None

    min_h, max_h = HEADCOUNT_RANGES.get(company_size, (None, None))
    if min_h:
        return min_h, max_h, 'estimated'
    return None, None, None


def _score_relevance(post):
    """Score post relevance 0-3."""
    title = post.get('title', '').lower()
    selftext = post.get('selftext', '').lower()
    text = f'{title} {selftext}'

    # 3: Direct layoff report
    has_layoff_kw = any(kw in text for kw in LAYOFF_KEYWORDS)
    has_company = post.get('_company') is not None
    if has_layoff_kw and has_company:
        return 3

    # Also 3 if title is very clearly about layoff
    if any(kw in title for kw in ['leépítés', 'leépít', 'elbocsát', 'layoff']):
        return 3

    # 2: Strong signal
    if has_layoff_kw or any(kw in text for kw in STRONG_SIGNAL_KEYWORDS):
        return 2

    # 1: Indirect signal
    if any(kw in text for kw in ANXIETY_KEYWORDS):
        return 1

    # 0: Not relevant
    return 0


def _detect_ai_attribution(post):
    """Check if AI is mentioned as cause of layoff/situation."""
    title = post.get('title', '').lower()
    selftext = post.get('selftext', '').lower()
    comments_text = ' '.join(
        c.get('body', '').lower() for c in post.get('top_comments', [])
    )
    full_text = f'{title} {selftext} {comments_text}'

    # Strong keywords — enough on their own
    for kw in AI_KEYWORDS_STRONG:
        if kw in full_text:
            for source, text in [('title', title), ('selftext', selftext), ('comments', comments_text)]:
                if kw in text:
                    idx = text.find(kw)
                    start = max(0, idx - 80)
                    end = min(len(text), idx + 80)
                    context = text[start:end].strip()
                    return True, f'[{source}] ...{context}...'
            return True, None

    # Context keywords — need to co-occur with job/layoff terms in the same post
    job_terms = ['munka', 'állás', 'leépít', 'elbocsát', 'fejlesztő', 'programozó',
                 'munkahely', 'elveszi', 'helyettesít', 'kiváltja', 'felesleg']
    has_job_context = any(jt in full_text for jt in job_terms)

    if has_job_context:
        for kw in AI_KEYWORDS_CONTEXT:
            # Use word boundary matching for short terms
            if len(kw) <= 3:
                pattern = r'\b' + re.escape(kw) + r'\b'
                match = re.search(pattern, full_text, re.IGNORECASE)
                if not match:
                    continue
            elif kw not in full_text:
                continue

            for source, text in [('title', title), ('selftext', selftext), ('comments', comments_text)]:
                if len(kw) <= 3:
                    match = re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE)
                    if not match:
                        continue
                    idx = match.start()
                elif kw not in text:
                    continue
                else:
                    idx = text.find(kw)
                start = max(0, idx - 80)
                end = min(len(text), idx + 80)
                context = text[start:end].strip()
                return True, f'[{source}] ...{context}...'
            return True, None

    return False, None


def _detect_hiring_freeze(post):
    """Check for hiring freeze signals."""
    title = post.get('title', '').lower()
    selftext = post.get('selftext', '').lower()
    comments_text = ' '.join(
        c.get('body', '').lower() for c in post.get('top_comments', [])
    )
    full_text = f'{title} {selftext} {comments_text}'

    return any(kw in full_text for kw in FREEZE_KEYWORDS)


def _categorize(post):
    """Categorize post: layoff / freeze / anxiety / other."""
    title = post.get('title', '').lower()
    selftext = post.get('selftext', '').lower()
    text = f'{title} {selftext}'

    if any(kw in text for kw in LAYOFF_KEYWORDS):
        return 'layoff'
    if any(kw in text for kw in FREEZE_KEYWORDS):
        return 'freeze'
    if any(kw in text for kw in ANXIETY_KEYWORDS):
        return 'anxiety'
    return 'other'


def analyze_posts(posts):
    """Analyze all posts. Returns enriched post list."""
    analyzed = []

    for post in posts:
        company, company_source, company_size, sector = _extract_company(post)
        post['_company'] = company  # temp field for relevance scoring

        hc_min, hc_max, hc_source = _extract_headcount(post)
        if hc_source is None and company is not None:
            hc_min, hc_max, hc_source = _estimate_headcount(company_size, post)
        elif hc_source is None:
            hc_min, hc_max, hc_source = _estimate_headcount(None, post)

        relevance = _score_relevance(post)
        ai_attributed, ai_context = _detect_ai_attribution(post)
        hiring_freeze = _detect_hiring_freeze(post)
        category = _categorize(post)

        analyzed_post = {
            'id': post['id'],
            'title': post['title'],
            'subreddit': post['subreddit'],
            'date': post['date'],
            'created_utc': post['created_utc'],
            'score': post['score'],
            'num_comments': post['num_comments'],
            'url': post['url'],
            'selftext': post.get('selftext', ''),
            'top_comments': post.get('top_comments', []),
            'company': company,
            'company_source': company_source,
            'company_sector': sector,
            'headcount_min': hc_min,
            'headcount_max': hc_max,
            'headcount_source': hc_source,
            'relevance': relevance,
            'ai_attributed': ai_attributed,
            'ai_context': ai_context,
            'hiring_freeze_signal': hiring_freeze,
            'category': category,
            'llm_validated': False,
        }
        analyzed.append(analyzed_post)
        del post['_company']

    # Print summary
    by_relevance = {}
    for p in analyzed:
        r = p['relevance']
        by_relevance[r] = by_relevance.get(r, 0) + 1

    print(f'\nAnalysis complete:')
    print(f'  Relevance 3 (direct layoff): {by_relevance.get(3, 0)}')
    print(f'  Relevance 2 (strong signal): {by_relevance.get(2, 0)}')
    print(f'  Relevance 1 (indirect):      {by_relevance.get(1, 0)}')
    print(f'  Relevance 0 (not relevant):  {by_relevance.get(0, 0)}')
    print(f'  AI attributed: {sum(1 for p in analyzed if p["ai_attributed"])}')
    print(f'  Hiring freeze: {sum(1 for p in analyzed if p["hiring_freeze_signal"])}')

    return analyzed


def save_analyzed_posts(posts, output_path='data/analyzed_posts.json'):
    """Save analyzed posts to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f'Saved {len(posts)} analyzed posts to {output_path}')


if __name__ == '__main__':
    with open('data/raw_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    analyzed = analyze_posts(posts)
    save_analyzed_posts(analyzed)
