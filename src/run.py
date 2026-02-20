"""Main entry point — runs scraper → analyzer → LLM validate → report → HTML pipeline."""

import json
import os

# Ensure we run from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

from src.scraper import run_scraper, save_raw_posts
from src.analyzer import analyze_posts, save_analyzed_posts
from src.llm_validator import validate_posts, save_validated_posts
from src.report import generate_report
from src.visualize import generate_html


PAGES_URL = 'https://tatargabor.github.io/hu-it-layoffs/report.html'


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

    # Step 1: Scrape
    print('\n[1/5] Reddit scrape indítása...')
    raw_posts = run_scraper()
    save_raw_posts(raw_posts, 'data/raw_posts.json')

    # Step 2: Analyze (keyword-based)
    print('\n[2/5] Posztok elemzése...')
    analyzed = analyze_posts(raw_posts)
    save_analyzed_posts(analyzed, 'data/analyzed_posts.json')

    # Step 3: LLM Validation
    print('\n[3/5] LLM validáció...')
    validated, llm_stats = validate_posts(analyzed)
    save_validated_posts(validated, 'data/validated_posts.json')

    # Save stats alongside
    with open('data/llm_stats.json', 'w') as f:
        json.dump(llm_stats, f, indent=2)

    # Step 4: Markdown Report
    print('\n[4/5] Markdown riport generálása...')
    generate_report(validated, 'data/report.md', llm_stats=llm_stats)

    # Step 5: HTML Dashboard
    print('\n[5/5] HTML dashboard generálása...')
    generate_html(validated, 'data/report.html', llm_stats=llm_stats)

    # Generate README.md
    _generate_readme()

    print('\n' + '=' * 60)
    print('  Kész!')
    print(f'  Nyers adatok:      data/raw_posts.json')
    print(f'  Elemzett adatok:   data/analyzed_posts.json')
    print(f'  Validált adatok:   data/validated_posts.json')
    print(f'  Riport (MD):       data/report.md')
    print(f'  Dashboard (HTML):  data/report.html')
    print(f'  README:            README.md')
    print('=' * 60)


if __name__ == '__main__':
    main()
