"""Report generator — markdown report from analyzed/validated posts."""

import json
from datetime import datetime
from collections import defaultdict


def _quarter(date_str):
    """Return 'YYYY QN' from date string."""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    q = (dt.month - 1) // 3 + 1
    return f'{dt.year} Q{q}'


def _all_quarters(start='2023 Q1', end=None):
    """Generate all quarters from start to end."""
    if end is None:
        now = datetime.now()
        end = f'{now.year} Q{(now.month - 1) // 3 + 1}'
    quarters = []
    year, q = int(start[:4]), int(start[-1])
    end_year, end_q = int(end[:4]), int(end[-1])
    while (year, q) <= (end_year, end_q):
        quarters.append(f'{year} Q{q}')
        q += 1
        if q > 4:
            q = 1
            year += 1
    return quarters


def _eff_relevance(post):
    """Effective relevance: llm_relevance if validated, else keyword relevance."""
    if post.get('llm_validated'):
        return post.get('llm_relevance', post.get('relevance', 0))
    return post.get('relevance', 0)


def _eff_headcount(post):
    """Effective headcount: llm_headcount if available, else keyword-based."""
    if post.get('llm_validated') and post.get('llm_headcount') is not None:
        hc = post['llm_headcount']
        return hc, hc, 'llm'
    return post.get('headcount_min'), post.get('headcount_max'), post.get('headcount_source')


def _headcount_str(post):
    """Format headcount as string."""
    hmin, hmax, src = _eff_headcount(post)
    if hmin is None:
        return '?'
    prefix = '~' if src == 'estimated' else ''
    if hmin == hmax:
        return f'{prefix}{hmin}'
    return f'{prefix}{hmin}-{hmax}'


def generate_report(posts, output_path='data/report.md'):
    """Generate full markdown report."""
    relevant = [p for p in posts if _eff_relevance(p) >= 1]
    strong = [p for p in posts if _eff_relevance(p) >= 2]
    direct = [p for p in posts if _eff_relevance(p) >= 3]

    lines = []

    # === SUMMARY ===
    lines.append('# Magyar IT Szektor Leépítések — Kimutatás')
    lines.append('')
    lines.append(f'*Generálva: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')
    lines.append(f'*Forrás: Reddit (r/programmingHungary, r/hungary) publikus adatok*')
    lines.append('')

    # Headcount FIRST
    total_min = sum((_eff_headcount(p)[0] or 0) for p in strong)
    total_max = sum((_eff_headcount(p)[1] or 0) for p in strong)
    if total_min > 0:
        lines.append(f'**Becsült összes érintett: ~{total_min}–{total_max} fő**')
    lines.append('')

    # Date range
    if relevant:
        dates = sorted(p['date'] for p in relevant)
        lines.append(f'**Időszak:** {dates[0]} – {dates[-1]}')
    lines.append(f'**Összes releváns poszt:** {len(relevant)}')
    lines.append(f'**Közvetlen leépítés riport (relevancia 3):** {len(direct)}')
    lines.append(f'**Erős jelzés (relevancia >= 2):** {len(strong)}')

    companies = set(p.get('company') or p.get('llm_company') for p in relevant if p.get('company') or p.get('llm_company'))
    lines.append(f'**Érintett cégek száma:** {len(companies)}')

    ai_count = sum(1 for p in relevant if p.get('ai_attributed'))
    lines.append(f'**AI-t említő posztok:** {ai_count}')

    freeze_count = sum(1 for p in relevant if p.get('hiring_freeze_signal'))
    lines.append(f'**Hiring freeze jelzések:** {freeze_count}')

    # LLM validation stats
    llm_count = sum(1 for p in relevant if p.get('llm_validated'))
    if llm_count > 0:
        lines.append(f'**LLM-validált posztok:** {llm_count}/{len(relevant)}')
    lines.append('')

    # === TIMELINE ===
    lines.append('## Negyedéves Timeline')
    lines.append('')

    quarters = _all_quarters()
    q_data = {q: [] for q in quarters}
    for p in strong:
        q = _quarter(p['date'])
        if q in q_data:
            q_data[q].append(p)

    lines.append('| Negyedév | Posztok | Cégek | Becsült fők | Események |')
    lines.append('|----------|---------|-------|-------------|-----------|')

    for q in quarters:
        qposts = q_data[q]
        if not qposts:
            lines.append(f'| {q} | 0 | — | — | Nincs adat |')
            continue

        q_companies = set(
            p.get('company') or p.get('llm_company')
            for p in qposts if p.get('company') or p.get('llm_company')
        )
        q_min = sum((_eff_headcount(p)[0] or 0) for p in qposts)
        q_max = sum((_eff_headcount(p)[1] or 0) for p in qposts)
        hc_str = f'~{q_min}–{q_max}' if q_min > 0 else '?'
        company_str = ', '.join(sorted(q_companies)) if q_companies else '?'
        events = '; '.join(p['title'][:40] for p in qposts[:3])
        if len(qposts) > 3:
            events += f'; +{len(qposts) - 3} más'

        lines.append(f'| {q} | {len(qposts)} | {company_str} | {hc_str} | {events} |')

    lines.append('')

    # === COMPANY TABLE ===
    lines.append('## Érintett Cégek')
    lines.append('')
    lines.append('| Cég | Dátum | Becsült fők | Szektor | AI-faktor | Forrás |')
    lines.append('|-----|-------|-------------|---------|-----------|--------|')

    company_posts = [p for p in strong if p.get('company') or p.get('llm_company')]
    company_posts.sort(key=lambda x: x['date'], reverse=True)

    for p in company_posts:
        company = p.get('company') or p.get('llm_company')
        ai_str = 'igen' if p.get('ai_attributed') else '—'
        link = f'[link]({p["url"]})'
        lines.append(
            f'| {company} | {p["date"]} | {_headcount_str(p)} | '
            f'{p.get("company_sector", "?")} | {ai_str} | {link} |'
        )

    # Posts without identified company
    unknown_posts = [p for p in strong if not p.get('company') and not p.get('llm_company')]
    if unknown_posts:
        lines.append('')
        lines.append('**Cég nélküli erős jelzések:**')
        for p in unknown_posts:
            lines.append(f'- [{p["date"]}] [{p["title"][:60]}]({p["url"]})')

    lines.append('')

    # === AGGREGATE STATS ===
    lines.append('## Összesített Statisztikák')
    lines.append('')

    by_cat = {}
    for p in relevant:
        cat = p.get('category', 'other')
        by_cat[cat] = by_cat.get(cat, 0) + 1

    lines.append('| Kategória | Posztok száma |')
    lines.append('|-----------|---------------|')
    cat_labels = {
        'layoff': 'Közvetlen leépítés',
        'freeze': 'Hiring freeze / álláspiac',
        'anxiety': 'Karrier aggodalom',
        'other': 'Egyéb',
    }
    for cat in ['layoff', 'freeze', 'anxiety', 'other']:
        label = cat_labels.get(cat, cat)
        lines.append(f'| {label} | {by_cat.get(cat, 0)} |')

    lines.append('')

    by_sector = {}
    for p in strong:
        sector = p.get('company_sector') or 'ismeretlen'
        by_sector[sector] = by_sector.get(sector, 0) + 1

    if by_sector:
        lines.append('**Szektorok szerinti megoszlás (erős jelzések):**')
        for sector, count in sorted(by_sector.items(), key=lambda x: -x[1]):
            lines.append(f'- {sector}: {count} poszt')
        lines.append('')

    # === TECHNOLOGIES & ROLES ===
    tech_counts = defaultdict(int)
    role_counts = defaultdict(int)
    for p in relevant:
        if p.get('llm_validated'):
            for t in p.get('llm_technologies', []):
                tech_counts[t] += 1
            for r in p.get('llm_roles', []):
                role_counts[r] += 1

    if tech_counts:
        lines.append('## Érintett Technológiák')
        lines.append('')
        for tech, count in sorted(tech_counts.items(), key=lambda x: -x[1])[:20]:
            lines.append(f'- {tech}: {count} poszt')
        lines.append('')

    if role_counts:
        lines.append('## Érintett Munkakörök')
        lines.append('')
        for role, count in sorted(role_counts.items(), key=lambda x: -x[1])[:15]:
            lines.append(f'- {role}: {count} poszt')
        lines.append('')

    # === TREND ANALYSIS ===
    lines.append('## Trend Elemzés')
    lines.append('')

    q_counts = [(q, len(q_data.get(q, []))) for q in quarters]
    recent_qs = q_counts[-4:]
    earlier_qs = q_counts[:-4] if len(q_counts) > 4 else []

    recent_avg = sum(c for _, c in recent_qs) / max(len(recent_qs), 1)
    earlier_avg = sum(c for _, c in earlier_qs) / max(len(earlier_qs), 1) if earlier_qs else 0

    if recent_avg > earlier_avg * 1.5:
        trend_str = '**GYORSULÁS** — az utóbbi negyedévekben jelentősen több leépítési hír jelent meg'
    elif recent_avg > earlier_avg:
        trend_str = '**Enyhe növekedés** — a leépítések üteme lassan emelkedik'
    elif recent_avg < earlier_avg * 0.5:
        trend_str = '**Csökkenés** — kevesebb leépítési hír az utóbbi időben'
    else:
        trend_str = '**Stabil** — a leépítések üteme nagyjából állandó'

    lines.append(f'**Általános trend:** {trend_str}')
    lines.append('')

    ai_posts_by_year = {}
    for p in relevant:
        year = p['date'][:4]
        if year not in ai_posts_by_year:
            ai_posts_by_year[year] = {'total': 0, 'ai': 0}
        ai_posts_by_year[year]['total'] += 1
        if p.get('ai_attributed'):
            ai_posts_by_year[year]['ai'] += 1

    lines.append('**AI-attribúció évenként:**')
    for year in sorted(ai_posts_by_year.keys()):
        d = ai_posts_by_year[year]
        pct = round(d['ai'] / d['total'] * 100) if d['total'] > 0 else 0
        lines.append(f'- {year}: {d["ai"]}/{d["total"]} poszt ({pct}%)')
    lines.append('')

    multi_count = sum(1 for p in strong if (p.get('company_sector') or '').lower() not in ('', 'ai/startup'))
    startup_count = sum(1 for p in strong if 'startup' in (p.get('company_sector') or '').lower())
    lines.append('**Cég típus:**')
    lines.append(f'- Multinacionális / nagyvállalat: {multi_count} esemény')
    lines.append(f'- Startup / KKV: {startup_count} esemény')
    lines.append('')

    # === HIRING SIGNALS ===
    lines.append('## Hiring Freeze / Álláspiac Jelzések')
    lines.append('')

    freeze_posts = [p for p in relevant if p.get('hiring_freeze_signal')]
    if freeze_posts:
        for p in sorted(freeze_posts, key=lambda x: x['date'], reverse=True):
            lines.append(f'### [{p["date"]}] {p["title"]}')
            lines.append(f'*r/{p["subreddit"]}* — score: {p["score"]}, {p["num_comments"]} komment')
            lines.append(f'[Link]({p["url"]})')
            selftext = p.get('selftext', '')
            if selftext:
                preview = selftext[:200].replace('\n', ' ').strip()
                lines.append(f'> {preview}...')
            lines.append('')
    else:
        lines.append('Nem találtunk explicit hiring freeze jelzéseket.')
        lines.append('')

    # === DETAILED TABLE ===
    lines.append('## Részletes Táblázat')
    lines.append('')
    lines.append('| Dátum | Cím | Cég | Létszám | Kategória | Score | Komment | Rel. | LLM Conf. | AI |')
    lines.append('|-------|-----|-----|---------|-----------|-------|---------|------|-----------|----|')

    for p in sorted(relevant, key=lambda x: x['date'], reverse=True):
        company = p.get('company') or p.get('llm_company') or '—'
        hc = _headcount_str(p)
        cat = p.get('category', 'other')
        rel = _eff_relevance(p)
        conf = f'{p["llm_confidence"]:.0%}' if p.get('llm_validated') else '—'
        ai_str = 'igen' if p.get('ai_attributed') else '—'
        title_short = p['title'][:50] + ('...' if len(p['title']) > 50 else '')
        lines.append(
            f'| {p["date"]} | [{title_short}]({p["url"]}) | {company} | {hc} | '
            f'{cat} | {p["score"]} | {p["num_comments"]} | {rel} | {conf} | {ai_str} |'
        )

    lines.append('')

    # === DATA SOURCES ===
    lines.append('## Források')
    lines.append('')
    lines.append(f'Összesen {len(relevant)} releváns poszt két subredditről:')
    lines.append('')

    for p in sorted(relevant, key=lambda x: x['date'], reverse=True):
        rel_marker = {3: '***', 2: '**', 1: '*'}.get(_eff_relevance(p), '')
        lines.append(
            f'- [{p["date"]}] [{p["title"][:70]}]({p["url"]}) '
            f'(score: {p["score"]}, {p["num_comments"]} komment) {rel_marker}'
        )

    lines.append('')
    lines.append('---')
    lines.append('*Relevancia jelölés: \\*\\*\\* = közvetlen leépítés, \\*\\* = erős jelzés, \\* = közvetett*')

    report = '\n'.join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f'Report written to {output_path} ({len(lines)} lines)')
    return report


if __name__ == '__main__':
    with open('data/validated_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    generate_report(posts)
