"""Main entry point — runs scraper → analyzer → LLM validate → report → HTML pipeline."""

import json
import os
from datetime import datetime, timedelta

# Ensure we run from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

from src.scraper import run_scraper, save_raw_posts
from src.analyzer import analyze_posts, save_analyzed_posts
from src.llm_validator import batch_triage, validate_posts, save_validated_posts
from src.report import generate_report
from src.visualize import generate_html


PAGES_URL = 'https://tatargabor.github.io/hu-it-layoffs/report.html'
FROZEN_PATH = 'persisted_data/frozen_posts.json'
FREEZE_AGE_DAYS = 60


def _load_frozen_posts(path=FROZEN_PATH):
    """Load frozen (old, validated) posts. Returns dict of {id: post}."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            posts = json.load(f)
        print(f'Loaded {len(posts)} frozen posts from {path}')
        return {p['id']: p for p in posts}
    except Exception as e:
        print(f'  Warning: could not load frozen posts: {e}')
        return {}


def _save_frozen_posts(frozen_dict, path=FROZEN_PATH):
    """Save frozen posts to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    posts_list = sorted(frozen_dict.values(), key=lambda x: x.get('created_utc', 0), reverse=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(posts_list, f, ensure_ascii=False, indent=2)
    print(f'Saved {len(posts_list)} frozen posts to {path}')


def _freeze_old_posts(validated, frozen_dict, age_days=FREEZE_AGE_DAYS):
    """Move old validated posts to frozen. Returns count of newly frozen."""
    cutoff = (datetime.now() - timedelta(days=age_days)).strftime('%Y-%m-%d')
    newly_frozen = 0
    for p in validated:
        pid = p['id']
        if pid in frozen_dict:
            continue
        if (p.get('llm_validated')
                and p.get('date', '9999') < cutoff
                and 'llm_hungarian_relevance' in p):
            frozen_dict[pid] = p
            newly_frozen += 1
    return newly_frozen


def _generate_readme(report_path='data/report.md', output_path='README.md'):
    """Copy report.md to README.md with a Pages link header."""
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()

    header = (
        f'> **[Interaktív dashboard megtekintése]({PAGES_URL})**\n'
        f'>\n'
        f'> Ez a riport automatikusan frissül naponta.\n\n'
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + report_content)

    print(f'README.md generated from {report_path}')


def main():
    print('=' * 60)
    print('  magyar.dev/layoffs — IT Leépítés Radar')
    print('=' * 60)

    os.makedirs('data', exist_ok=True)
    os.makedirs('persisted_data', exist_ok=True)

    # Load frozen posts (old, validated, won't be re-processed)
    frozen = _load_frozen_posts()
    frozen_ids = set(frozen.keys())

    # Step 1: Scrape (skip frozen posts in fetch_post_details)
    print('\n[1/7] Multi-source scrape indítása...')
    raw_posts = run_scraper(frozen_ids=frozen_ids)
    save_raw_posts(raw_posts, 'data/raw_posts.json')

    # Step 2: Analyze (keyword-based)
    print('\n[2/7] Posztok elemzése...')
    analyzed = analyze_posts(raw_posts)
    save_analyzed_posts(analyzed, 'data/analyzed_posts.json')

    # Step 3: Batch LLM Triage (skip frozen)
    print('\n[3/7] Batch LLM triage...')
    triage_results = batch_triage(analyzed, frozen_ids=frozen_ids)

    # Step 4: LLM Validation (skip frozen)
    print('\n[4/7] LLM validáció...')
    validated, llm_stats = validate_posts(analyzed, triage_results=triage_results, frozen_ids=frozen_ids)

    # Merge: frozen + fresh validated
    frozen_list = list(frozen.values())
    all_validated = frozen_list + validated
    save_validated_posts(all_validated, 'data/validated_posts.json')
    print(f'  Merged: {len(frozen_list)} frozen + {len(validated)} fresh = {len(all_validated)} total')

    # Save stats alongside
    with open('data/llm_stats.json', 'w') as f:
        json.dump(llm_stats, f, indent=2)

    # Step 5: Freeze old validated posts
    print('\n[5/7] Régi posztok fagyasztása...')
    newly_frozen = _freeze_old_posts(all_validated, frozen)
    if newly_frozen > 0:
        _save_frozen_posts(frozen)
        print(f'  {newly_frozen} új poszt fagyasztva (összesen: {len(frozen)})')
    else:
        print(f'  Nincs új fagyasztandó poszt (összesen: {len(frozen)})')

    # Step 6: Markdown Report
    print('\n[6/7] Markdown riport generálása...')
    generate_report(all_validated, 'data/report.md', llm_stats=llm_stats)

    # Step 7: HTML Dashboard
    print('\n[7/7] HTML dashboard generálása...')
    generate_html(all_validated, 'data/report.html', llm_stats=llm_stats)

    # Generate README.md
    _generate_readme()

    print('\n' + '=' * 60)
    print('  Kész!')
    print(f'  Fagyasztott posztok: persisted_data/frozen_posts.json ({len(frozen)})')
    print(f'  Nyers adatok:       data/raw_posts.json')
    print(f'  Elemzett adatok:    data/analyzed_posts.json')
    print(f'  Validált adatok:    data/validated_posts.json ({len(all_validated)})')
    print(f'  Riport (MD):        data/report.md')
    print(f'  Dashboard (HTML):   data/report.html')
    print(f'  README:             README.md')
    print('=' * 60)


if __name__ == '__main__':
    main()
