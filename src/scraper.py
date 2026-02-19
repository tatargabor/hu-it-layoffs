"""Reddit scraper for Hungarian IT layoff posts using old.reddit.com JSON API."""

import json
import time
import urllib.request
import urllib.parse
from datetime import datetime


SUBREDDIT_QUERIES = {
    'programmingHungary': [
        'elbocsátás OR leépítés OR kirúgás OR létszámcsökkentés',
        'layoff OR fired OR hiring freeze',
        'elbocsát OR leépít',
        'bújtatott leépítés OR quiet firing',
        'AI elveszi OR AI munka OR AI munkahely',
        'álláskereső OR álláspiac',
        'munkanélküli OR nincs munka',
        # Known affected companies
        'OTP leépítés OR Ericsson leépítés OR NNG leépítés',
        'Szállás Group OR Docler OR Byborg',
        'Continental layoff OR Microsoft leépít OR Lensa',
    ],
    'hungary': [
        'IT leépítés OR programozó elbocsátás OR tech leépítés',
        'IT munkaerőpiac',
        'szoftver leépítés OR informatikus elbocsátás',
    ],
}

USER_AGENT = 'hu-it-layoff-report/1.0 (research project)'
REQUEST_DELAY = 2.0
RETRY_DELAY = 10
MAX_PAGES_PER_QUERY = 5
RESULTS_PER_PAGE = 100


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
            except urllib.error.HTTPError as e2:
                print(f'  Still 429 after retry, skipping: {url[:80]}')
                return None
        else:
            print(f'  HTTP {e.code} error: {url[:80]}')
            return None
    except Exception as e:
        print(f'  Error fetching {url[:80]}: {e}')
        return None


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
                'date': datetime.fromtimestamp(d['created_utc']).strftime('%Y-%m-%d'),
                'created_utc': d['created_utc'],
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
    """Fetch full selftext and top comments for a post."""
    post_id = post['id']
    subreddit = post['subreddit']
    url = f'https://old.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=20&sort=top'

    time.sleep(REQUEST_DELAY)
    data = _fetch_json(url)
    if not data or not isinstance(data, list) or len(data) < 2:
        post['top_comments'] = []
        return post

    # First element is the post itself
    post_data = data[0].get('data', {}).get('children', [])
    if post_data:
        full_selftext = post_data[0].get('data', {}).get('selftext', '')
        if full_selftext:
            post['selftext'] = full_selftext

    # Second element is the comment listing
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


def run_scraper():
    """Main scraper function. Returns list of unique posts with details."""
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

    print(f'\nTotal unique posts: {len(all_posts)}')
    print('Fetching post details (comments)...')

    posts_list = sorted(all_posts.values(), key=lambda x: x['created_utc'], reverse=True)

    for i, post in enumerate(posts_list):
        print(f'  [{i+1}/{len(posts_list)}] {post["title"][:60]}...')
        fetch_post_details(post)

    return posts_list


def save_raw_posts(posts, output_path='data/raw_posts.json'):
    """Save raw posts to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f'Saved {len(posts)} posts to {output_path}')


if __name__ == '__main__':
    posts = run_scraper()
    save_raw_posts(posts)
