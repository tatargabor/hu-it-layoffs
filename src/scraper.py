"""Multi-source scraper for Hungarian IT layoff posts.

Supported sources: Reddit (old.reddit.com JSON API), HUP.hu (HTML scraping), Google News (RSS).
Active sources controlled by ENABLED_SOURCES config (default: Reddit only).
"""

import hashlib
import json
import os
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser


# === CONFIGURATION ===

SUBREDDIT_QUERIES = {
    'programmingHungary': [
        'elbocsátás OR leépítés OR kirúgás OR létszámcsökkentés',
        'layoff OR fired OR hiring freeze',
        'elbocsát OR leépít',
        'bújtatott leépítés OR quiet firing',
        'AI elveszi OR AI munka OR AI munkahely',
        'álláskereső OR álláspiac',
        'munkanélküli IT OR nincs munka programozó OR nincs munka fejlesztő',
        # Known affected companies
        'OTP leépítés OR Ericsson leépítés OR NNG leépítés',
        'Szállás Group OR Docler OR Byborg',
        'Continental layoff OR Microsoft leépít OR Lensa',
    ],
    'hungary': [
        'IT leépítés OR programozó elbocsátás OR tech leépítés',
        'IT munkaerőpiac',
        'szoftver leépítés OR informatikus elbocsátás',
        'álláskereső OR álláspiac',
        'hiring freeze',
        'Ericsson OR Continental OR OTP OR NNG OR Lensa OR Microsoft leépítés',
    ],
    'layoffs': [
        'Hungary OR Hungarian OR Budapest',
    ],
    'cscareerquestions': [
        'Hungary OR Hungarian OR Budapest',
    ],
}

HUP_QUERIES = [
    'leépítés',
    'elbocsátás',
    'IT munkahely',
    'hiring freeze',
]

GNEWS_QUERIES = [
    # Magyar IT leépítés
    'leépítés IT',
    'elbocsátás programozó',
    'leépítés informatikus',
    # AI / munkahely
    'mesterséges intelligencia munkahely',
    'AI leépítés',
    # Angol query-k magyar kontextussal
    'tech layoff Hungary',
    'AI jobs Budapest',
    # Hiring freeze
    'hiring freeze Magyarország',
    # Cégspecifikus
    'Ericsson leépítés',
    'Audi leépítés',
    'Continental leépítés',
    'OTP leépítés',
]

# Which sources to scrape. Valid values: 'reddit', 'google-news', 'hup'
ENABLED_SOURCES = ['reddit', 'google-news']

USER_AGENT = 'hu-it-layoff-report/1.0 (research project)'
REQUEST_DELAY = 2.0
RETRY_DELAY = 10
MAX_PAGES_PER_QUERY = 5
RESULTS_PER_PAGE = 100


# === HTTP HELPERS ===

def _fetch_json(url):
    """Fetch JSON from URL with rate limiting and retry on 429."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f'  Rate limited (429), waiting {RETRY_DELAY}s...')
            time.sleep(RETRY_DELAY)
            try:
                resp = urllib.request.urlopen(req, timeout=30)
                return json.loads(resp.read())
            except urllib.error.HTTPError:
                print(f'  Still 429 after retry, skipping: {url[:80]}')
                return None
        else:
            print(f'  HTTP {e.code} error: {url[:80]}')
            return None
    except Exception as e:
        print(f'  Error fetching {url[:80]}: {e}')
        return None


def _fetch_html(url):
    """Fetch HTML from URL with rate limiting."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'  Error fetching {url[:80]}: {e}')
        return None


# === REDDIT SCRAPER ===

def search_subreddit(subreddit, query):
    """Search a subreddit with pagination. Returns list of post dicts."""
    posts = []
    after = None

    for page in range(MAX_PAGES_PER_QUERY):
        encoded_q = urllib.parse.quote(query)
        url = (
            f'https://old.reddit.com/r/{subreddit}/search.json'
            f'?q={encoded_q}&restrict_sr=on&sort=new&limit={RESULTS_PER_PAGE}'
        )
        if after:
            url += f'&after={after}'

        time.sleep(REQUEST_DELAY)
        data = _fetch_json(url)
        if not data:
            break

        children = data.get('data', {}).get('children', [])
        if not children:
            break

        for child in children:
            d = child['data']
            posts.append({
                'id': d['id'],
                'title': d.get('title', ''),
                'subreddit': d.get('subreddit', subreddit),
                'source': 'reddit',
                'date': datetime.fromtimestamp(d['created_utc']).strftime('%Y-%m-%d'),
                'created_utc': d['created_utc'],
                'edited': d.get('edited', False),
                'score': d.get('score', 0),
                'num_comments': d.get('num_comments', 0),
                'url': f"https://reddit.com{d.get('permalink', '')}",
                'selftext': d.get('selftext', ''),
            })

        after = data.get('data', {}).get('after')
        if not after or len(children) < RESULTS_PER_PAGE:
            break

        print(f'    Page {page + 2}...')

    return posts


def fetch_post_details(post):
    """Fetch full selftext and top comments for a Reddit post."""
    if post.get('source') != 'reddit':
        return post

    post_id = post['id']
    subreddit = post['subreddit']
    url = f'https://old.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=20&sort=top'

    time.sleep(REQUEST_DELAY)
    data = _fetch_json(url)
    if not data or not isinstance(data, list) or len(data) < 2:
        post['top_comments'] = []
        return post

    post_data = data[0].get('data', {}).get('children', [])
    if post_data:
        full_selftext = post_data[0].get('data', {}).get('selftext', '')
        if full_selftext:
            post['selftext'] = full_selftext

    comments = []
    comment_children = data[1].get('data', {}).get('children', [])
    for c in comment_children[:20]:
        if c.get('kind') != 't1':
            continue
        cd = c.get('data', {})
        body = cd.get('body', '')
        if body:
            comments.append({
                'author': cd.get('author', '[deleted]'),
                'body': body,
                'score': cd.get('score', 0),
            })

    post['top_comments'] = comments
    return post


def run_reddit_scraper():
    """Scrape all configured Reddit subreddits. Returns dict of {id: post}."""
    all_posts = {}

    for subreddit, queries in SUBREDDIT_QUERIES.items():
        print(f'\n=== r/{subreddit} ===')
        for query in queries:
            print(f'  Searching: "{query}"')
            posts = search_subreddit(subreddit, query)
            new_count = 0
            for p in posts:
                if p['id'] not in all_posts:
                    all_posts[p['id']] = p
                    new_count += 1
            print(f'    Found {len(posts)}, {new_count} new (total: {len(all_posts)})')

    return all_posts


# === HUP.HU SCRAPER ===

class _HupSearchParser(HTMLParser):
    """Parse HUP.hu search results page to extract topic links."""

    def __init__(self):
        super().__init__()
        self.results = []  # list of (url, title)
        self._in_result_link = False
        self._current_href = None
        self._current_title = ''

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if '/node/' in href and 'search' not in href:
                self._in_result_link = True
                self._current_href = href
                self._current_title = ''

    def handle_data(self, data):
        if self._in_result_link:
            self._current_title += data

    def handle_endtag(self, tag):
        if tag == 'a' and self._in_result_link:
            self._in_result_link = False
            if self._current_href and self._current_title.strip():
                self.results.append((self._current_href, self._current_title.strip()))
            self._current_href = None
            self._current_title = ''


class _HupTopicParser(HTMLParser):
    """Parse a HUP.hu topic page to extract body text and metadata."""

    def __init__(self):
        super().__init__()
        self.body_text = ''
        self.date_str = ''
        self.comment_count = 0
        self._in_content = False
        self._in_submitted = False
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')
        if 'content' in cls and tag == 'div':
            self._in_content = True
            self._depth = 0
        if self._in_content and tag in ('div', 'p', 'span'):
            self._depth += 1
        if 'submitted' in cls:
            self._in_submitted = True

    def handle_data(self, data):
        if self._in_content:
            self.body_text += data
        if self._in_submitted:
            self.date_str += data

    def handle_endtag(self, tag):
        if self._in_content and tag in ('div', 'p', 'span'):
            self._depth -= 1
            if self._depth <= 0:
                self._in_content = False
        if self._in_submitted and tag in ('div', 'span', 'p'):
            self._in_submitted = False


def _parse_hup_date(date_text):
    """Try to extract a date from HUP submitted text like '2024. január 15.'"""
    import re
    months = {
        'január': 1, 'február': 2, 'március': 3, 'április': 4,
        'május': 5, 'június': 6, 'július': 7, 'augusztus': 8,
        'szeptember': 9, 'október': 10, 'november': 11, 'december': 12,
    }
    # Pattern: YYYY. hónap DD.
    m = re.search(r'(\d{4})\.\s*(\w+)\s+(\d{1,2})\.?', date_text)
    if m:
        year = int(m.group(1))
        month_name = m.group(2).lower()
        day = int(m.group(3))
        month = months.get(month_name, 1)
        try:
            return datetime(year, month, day).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return datetime.now().strftime('%Y-%m-%d')


def _hup_node_id(url):
    """Extract node ID from HUP URL like /node/12345."""
    import re
    m = re.search(r'/node/(\d+)', url)
    return m.group(1) if m else url.split('/')[-1]


def run_hup_scraper():
    """Scrape HUP.hu forum for IT layoff related topics. Returns dict of {id: post}."""
    all_posts = {}

    print('\n=== hup.hu ===')

    for query in HUP_QUERIES:
        encoded_q = urllib.parse.quote(query)
        search_url = f'https://hup.hu/search/node/{encoded_q}'
        print(f'  Searching: "{query}"')

        time.sleep(REQUEST_DELAY)
        html = _fetch_html(search_url)
        if not html:
            print(f'    HUP.hu unreachable, skipping')
            continue

        parser = _HupSearchParser()
        try:
            parser.feed(html)
        except Exception as e:
            print(f'    Parse error: {e}, skipping')
            continue

        new_count = 0
        for href, title in parser.results[:20]:  # limit per query
            node_id = _hup_node_id(href)
            post_id = f'hup-{node_id}'

            if post_id in all_posts:
                continue

            # Fetch topic page
            topic_url = href if href.startswith('http') else f'https://hup.hu{href}'
            time.sleep(REQUEST_DELAY)
            topic_html = _fetch_html(topic_url)

            body = ''
            date = datetime.now().strftime('%Y-%m-%d')
            if topic_html:
                tp = _HupTopicParser()
                try:
                    tp.feed(topic_html)
                    body = tp.body_text.strip()[:2000]
                    if tp.date_str:
                        date = _parse_hup_date(tp.date_str)
                except Exception:
                    pass

            all_posts[post_id] = {
                'id': post_id,
                'title': title,
                'subreddit': 'hup.hu',
                'source': 'hup.hu',
                'date': date,
                'created_utc': datetime.strptime(date, '%Y-%m-%d').timestamp(),
                'score': 0,
                'num_comments': 0,
                'url': topic_url,
                'selftext': body,
                'top_comments': [],
            }
            new_count += 1

        print(f'    Found {len(parser.results)} results, {new_count} new (total: {len(all_posts)})')

    return all_posts


# === GOOGLE NEWS ARTICLE EXTRACTION ===

GNEWS_DECODE_DELAY = 1.5  # seconds between googlenewsdecoder calls

def _decode_gnews_url(gnews_url):
    """Decode a Google News RSS URL to the real article URL. Returns real URL or None."""
    try:
        from googlenewsdecoder import new_decoderv1
        time.sleep(GNEWS_DECODE_DELAY)
        result = new_decoderv1(gnews_url, interval=None)
        if result.get('status'):
            return result['decoded_url']
    except Exception as e:
        print(f'    GNews decode error: {e}')
    return None


def _extract_article_content(url):
    """Extract article body text from a URL using trafilatura. Returns text or empty string."""
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ''
        text = trafilatura.extract(downloaded, include_comments=False)
        if text and len(text) >= 50:
            return text
    except Exception as e:
        print(f'    Article extract error: {e}')
    return ''


# === GOOGLE NEWS SCRAPER ===

def _parse_pubdate(pubdate_str):
    """Parse RFC 2822 pubDate string to (date_str, timestamp)."""
    try:
        dt = parsedate_to_datetime(pubdate_str)
        return dt.strftime('%Y-%m-%d'), dt.timestamp()
    except Exception:
        now = datetime.now()
        return now.strftime('%Y-%m-%d'), now.timestamp()


def _gnews_post_id(title, date_str):
    """Generate deterministic ID from title + date."""
    raw = f'{title}{date_str}'.encode('utf-8')
    return f'gnews-{hashlib.sha256(raw).hexdigest()[:10]}'


def run_google_news_scraper():
    """Scrape Google News RSS for IT layoff related articles. Returns dict of {id: post}."""
    all_posts = {}

    print('\n=== Google News RSS ===')

    for query in GNEWS_QUERIES:
        encoded_q = urllib.parse.quote(query)
        rss_url = f'https://news.google.com/rss/search?q={encoded_q}&hl=hu&gl=HU&ceid=HU:hu'
        print(f'  Searching: "{query}"')

        time.sleep(REQUEST_DELAY)
        xml_text = _fetch_html(rss_url)
        if not xml_text:
            print(f'    Google News unreachable, skipping')
            continue

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            print(f'    XML parse error: {e}, skipping')
            continue

        new_count = 0
        for item in root.iter('item'):
            title_el = item.find('title')
            link_el = item.find('link')
            pubdate_el = item.find('pubDate')
            source_el = item.find('source')

            title = title_el.text.strip() if title_el is not None and title_el.text else ''
            if not title:
                continue

            link = link_el.text.strip() if link_el is not None and link_el.text else ''
            pubdate = pubdate_el.text.strip() if pubdate_el is not None and pubdate_el.text else ''
            news_source = source_el.text.strip() if source_el is not None and source_el.text else 'unknown'

            date_str, timestamp = _parse_pubdate(pubdate)
            post_id = _gnews_post_id(title, date_str)

            if post_id in all_posts:
                continue

            all_posts[post_id] = {
                'id': post_id,
                'title': title,
                'subreddit': 'google-news',
                'source': 'google-news',
                'news_source': news_source,
                'date': date_str,
                'created_utc': timestamp,
                'score': 0,
                'num_comments': 0,
                'url': link,
                'selftext': '',
                'top_comments': [],
            }
            new_count += 1

        print(f'    Found {new_count} new (total: {len(all_posts)})')

    # Fetch article content for new posts
    new_posts = [p for p in all_posts.values() if not p.get('selftext')]
    if new_posts:
        print(f'\n  Fetching article content for {len(new_posts)} Google News posts...')
        fetched = 0
        for i, post in enumerate(new_posts):
            real_url = _decode_gnews_url(post['url'])
            if real_url:
                post['url'] = real_url  # replace GN redirect with real URL
                content = _extract_article_content(real_url)
                if content:
                    post['selftext'] = content
                    fetched += 1
            if (i + 1) % 10 == 0:
                print(f'    Progress: {i + 1}/{len(new_posts)} ({fetched} with content)')
        print(f'  Article content: {fetched}/{len(new_posts)} successfully extracted')

    return all_posts


# === MAIN ORCHESTRATION ===

def _load_existing_posts(path='data/raw_posts.json'):
    """Load existing raw_posts.json for incremental merge."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            posts = json.load(f)
        return {p['id']: p for p in posts}
    except Exception as e:
        print(f'  Warning: could not load existing posts: {e}')
        return {}


def _merge_posts(existing, new_posts):
    """Merge new posts into existing. Updates fields for known posts, adds new ones."""
    added = 0
    updated = 0
    for pid, post in new_posts.items():
        if pid in existing:
            # Update mutable fields
            existing[pid]['score'] = post.get('score', existing[pid].get('score', 0))
            existing[pid]['num_comments'] = post.get('num_comments', existing[pid].get('num_comments', 0))
            if post.get('selftext'):
                existing[pid]['selftext'] = post['selftext']
            if post.get('top_comments'):
                existing[pid]['top_comments'] = post['top_comments']
            # Ensure source field exists on old posts
            if 'source' not in existing[pid]:
                existing[pid]['source'] = post.get('source', 'reddit')
            updated += 1
        else:
            existing[pid] = post
            added += 1
    return existing, added, updated


def run_scraper(frozen_ids=None):
    """Main scraper: runs enabled sources (controlled by ENABLED_SOURCES), with incremental merge.

    Args:
        frozen_ids: set of post IDs to skip in fetch_post_details (already frozen/validated).
    """
    if frozen_ids is None:
        frozen_ids = set()

    # Log enabled/skipped sources
    all_sources = ['reddit', 'google-news', 'hup']
    enabled = [s for s in all_sources if s in ENABLED_SOURCES]
    skipped = [s for s in all_sources if s not in ENABLED_SOURCES]
    print(f'Sources: {", ".join(s + " (enabled)" for s in enabled)}'
          f'{", " + ", ".join(s + " (skipped)" for s in skipped) if skipped else ""}')

    # Load existing data
    existing = _load_existing_posts()
    if existing:
        print(f'Loaded {len(existing)} existing posts for incremental update')

    # Scrape Reddit
    reddit_posts = run_reddit_scraper() if 'reddit' in ENABLED_SOURCES else {}

    # Scrape HUP.hu
    hup_posts = run_hup_scraper() if 'hup' in ENABLED_SOURCES else {}

    # Scrape Google News
    gnews_posts = run_google_news_scraper() if 'google-news' in ENABLED_SOURCES else {}

    # Merge all sources
    all_new = {**reddit_posts, **hup_posts, **gnews_posts}
    merged, added, updated = _merge_posts(existing, all_new)

    print(f'\nMerge: {added} new, {updated} updated, {len(merged)} total')

    # Fetch details for Reddit posts that need it (skip frozen)
    print('Fetching post details (comments)...')
    posts_list = sorted(merged.values(), key=lambda x: x.get('created_utc', 0), reverse=True)

    skipped_frozen = 0
    skipped_has_comments = 0
    fetched = 0
    for i, post in enumerate(posts_list):
        if post.get('source') != 'reddit':
            continue
        if post['id'] in frozen_ids:
            skipped_frozen += 1
            continue
        # Skip if already have comments from previous run (not a new post)
        if post.get('top_comments') and post['id'] not in reddit_posts:
            skipped_has_comments += 1
            continue
        if post['id'] in reddit_posts:
            print(f'  [{i+1}/{len(posts_list)}] {post["title"][:60]}...')
            fetch_post_details(post)
            fetched += 1

    print(f'  Fetched details: {fetched}, skipped frozen: {skipped_frozen}, skipped (has comments): {skipped_has_comments}')

    return posts_list


def save_raw_posts(posts, output_path='data/raw_posts.json'):
    """Save raw posts to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f'Saved {len(posts)} posts to {output_path}')


if __name__ == '__main__':
    posts = run_scraper()
    save_raw_posts(posts)
