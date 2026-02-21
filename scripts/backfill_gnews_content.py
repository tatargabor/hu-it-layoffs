"""Backfill article content for existing Google News posts with empty selftext."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.scraper import _decode_gnews_url, _extract_article_content


def main():
    path = 'data/validated_posts.json'
    with open(path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    gn_empty = [p for p in posts if p.get('source') == 'google-news' and not p.get('selftext', '').strip()]
    print(f'Found {len(gn_empty)} Google News posts with empty selftext (out of {len(posts)} total)')

    if not gn_empty:
        print('Nothing to backfill.')
        return

    success = 0
    fail_decode = 0
    fail_extract = 0

    for i, post in enumerate(gn_empty):
        title = post['title'][:50]
        real_url = _decode_gnews_url(post['url'])
        if not real_url:
            fail_decode += 1
            print(f'  [{i+1}/{len(gn_empty)}] DECODE FAIL | {title}')
            continue

        post['url'] = real_url
        content = _extract_article_content(real_url)
        if content:
            post['selftext'] = content
            success += 1
            print(f'  [{i+1}/{len(gn_empty)}] OK ({len(content)} ch) | {title}')
        else:
            fail_extract += 1
            print(f'  [{i+1}/{len(gn_empty)}] EXTRACT FAIL | {title}')

        if (i + 1) % 50 == 0:
            # Save progress periodically
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            print(f'  --- Saved progress: {success} backfilled so far ---')

    # Final save
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f'\n=== Backfill complete ===')
    print(f'  Success: {success}/{len(gn_empty)}')
    print(f'  Decode fail: {fail_decode}')
    print(f'  Extract fail: {fail_extract}')


if __name__ == '__main__':
    main()
