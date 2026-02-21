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


def _is_hungarian_relevant(post):
    """Check if post has Hungarian relevance (not 'none'). Posts without the field are assumed relevant."""
    return post.get('llm_hungarian_relevance', 'direct') != 'none'


# Sectors where layoffs count as IT-relevant only if IT roles/tech mentioned
_NON_IT_SECTORS = {'automotive', 'other', 'energy', 'retail', 'manufacturing'}
_IT_ROLE_KEYWORDS = {'fejlesztő', 'programozó', 'informatikus', 'szoftver', 'devops', 'qa',
                     'developer', 'engineer', 'software', 'IT', 'data', 'backend', 'frontend'}


def _is_it_relevant(post):
    """Filter out non-IT sector layoffs unless IT roles/technologies are mentioned."""
    sector = _eff_sector(post)
    if sector not in _NON_IT_SECTORS:
        return True
    # Non-IT sector: check if IT roles or technologies mentioned
    roles = post.get('llm_roles', [])
    techs = post.get('llm_technologies', [])
    summary = post.get('llm_summary', '')
    text = ' '.join(roles + techs) + ' ' + summary
    return any(kw in text.lower() for kw in _IT_ROLE_KEYWORDS)


def _count_events(posts):
    """Count unique events. Posts with same event_label count as 1. Posts without label count individually."""
    labels = set()
    count = 0
    for p in posts:
        label = p.get('llm_event_label')
        if label:
            if label not in labels:
                labels.add(label)
                count += 1
        else:
            count += 1
    return count


def _event_groups(posts):
    """Group posts by event_label. Returns list of (label, [posts]) tuples.
    Posts without label get their own group (label=None)."""
    groups = {}
    ungrouped = []
    for p in posts:
        label = p.get('llm_event_label')
        if label:
            groups.setdefault(label, []).append(p)
        else:
            ungrouped.append(p)
    result = list(groups.items())
    for p in ungrouped:
        result.append((None, [p]))
    return result


def _is_ai_attributed(post):
    """Check if post is AI-attributed. Uses LLM ai_role if available, else keyword."""
    if post.get('llm_validated') and 'llm_ai_role' in post:
        return post['llm_ai_role'] in ('direct', 'factor', 'concern')
    return post.get('ai_attributed', False)


def _eff_sector(post):
    """Effective sector: llm_sector if validated, else analyzer company_sector, else 'ismeretlen'."""
    if post.get('llm_validated') and 'llm_sector' in post and post['llm_sector']:
        return post['llm_sector']
    return post.get('company_sector') or 'ismeretlen'


_GENERIC_COMPANY_PATTERNS = ['nagyobb', 'kisebb', 'egy cég', 'élelmiszerlánc', 'nem nevezett']


def _is_named_company(name):
    """Filter out generic/unnamed company references from stats."""
    if not name:
        return False
    lower = name.lower()
    return not any(p in lower for p in _GENERIC_COMPANY_PATTERNS)


def _source_str(post):
    """Format source as display string."""
    source = post.get('source', 'reddit')
    if source == 'reddit':
        return f'r/{post.get("subreddit", "?")}'
    if source == 'google-news':
        return post.get('news_source', 'unknown')
    return source


def _group_by_event(posts):
    """Group posts by event_label. Returns list of (label, representative, other_posts).

    Representative selection: Reddit > highest relevance > most recent.
    Posts without event_label get their own group (other_posts=[]).
    """
    groups = {}
    result = []
    for p in posts:
        label = p.get('llm_event_label')
        if label:
            groups.setdefault(label, []).append(p)
        else:
            result.append((None, p, []))

    for label, group_posts in groups.items():
        group_posts.sort(key=lambda x: (
            0 if x.get('source') == 'reddit' else 1,
            -_eff_relevance(x),
            -x.get('created_utc', 0),
        ))
        rep = group_posts[0]
        others = group_posts[1:]
        result.append((label, rep, others))

    result.sort(key=lambda x: x[1].get('created_utc', 0), reverse=True)
    return result


def generate_report(posts, output_path='data/report.md', llm_stats=None):
    """Generate full markdown report."""
    relevant = [p for p in posts if _eff_relevance(p) >= 1 and _is_hungarian_relevant(p) and _is_it_relevant(p)]
    strong = [p for p in posts if _eff_relevance(p) >= 2 and _is_hungarian_relevant(p) and _is_it_relevant(p)]
    direct = [p for p in posts if _eff_relevance(p) >= 3 and _is_hungarian_relevant(p) and _is_it_relevant(p)]

    lines = []

    # === SUMMARY ===
    lines.append('# Magyar IT Szektor Leépítések — Kimutatás')
    lines.append('')
    lines.append('**[Interaktív Dashboard](https://tatargabor.github.io/hu-it-layoffs/report.html)** | [GitHub repo](https://github.com/tatargabor/hu-it-layoffs)')
    lines.append('')
    lines.append(f'*Generálva: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Forrás: Reddit + Google News publikus adatok*')
    lines.append('')
    lines.append('> **Jogi nyilatkozat:** Ez a kimutatás publikusan elérhető posztok és hírek automatizált elemzése. A tartalom harmadik felek által közzétett véleményeket és információkat tükrözi, amelyek pontossága nem ellenőrzött. A kimutatás tájékoztató és kutatási célú, nem minősül tényállításnak egyetlen szervezetről sem. Tartalom eltávolítását a [GitHub Issues](https://github.com/tatargabor/hu-it-layoffs/issues) oldalon lehet kérni.')
    lines.append('>')
    lines.append('> **Disclaimer:** This report is an automated analysis of publicly available posts and news articles. It reflects opinions and information published by third parties, the accuracy of which has not been verified. This report is for informational and research purposes only and does not constitute factual claims about any organization. Content removal requests can be submitted via [GitHub Issues](https://github.com/tatargabor/hu-it-layoffs/issues).')
    lines.append('')

    # Date range
    if relevant:
        dates = sorted(p['date'] for p in relevant)
        lines.append(f'**Időszak:** {dates[0]} – {dates[-1]}')
    event_count = _count_events(relevant)
    lines.append(f'**Összes releváns poszt:** {len(relevant)} ({event_count} egyedi esemény)')
    lines.append(f'**Közvetlen leépítés riport (relevancia 3):** {_count_events(direct)} esemény')
    lines.append(f'**Erős jelzés (relevancia >= 2):** {_count_events(strong)} esemény')

    companies = set(c for p in relevant for c in [p.get('company') or p.get('llm_company')] if _is_named_company(c))
    lines.append(f'**Érintett cégek száma:** {len(companies)}')

    ai_count = sum(1 for p in relevant if _is_ai_attributed(p))
    lines.append(f'**AI-t említő posztok:** {ai_count}')

    freeze_count = sum(1 for p in relevant if p.get('hiring_freeze_signal'))
    lines.append(f'**Hiring freeze jelzések:** {freeze_count}')

    total_score = sum(p.get('score', 0) for p in relevant)
    total_comments = sum(p.get('num_comments', 0) for p in relevant)
    lines.append(f'**Összes reakció:** {total_score:,} upvote, {total_comments:,} komment')

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

    lines.append('| Negyedév | Posztok | Score | Komment | Cégek | Események |')
    lines.append('|----------|---------|-------|---------|-------|-----------|')

    for q in quarters:
        qposts = q_data[q]
        if not qposts:
            lines.append(f'| {q} | 0 | — | — | — | Nincs adat |')
            continue

        q_score = sum(p.get('score', 0) for p in qposts)
        q_comments = sum(p.get('num_comments', 0) for p in qposts)
        q_companies = set(
            p.get('company') or p.get('llm_company')
            for p in qposts if p.get('company') or p.get('llm_company')
        )
        company_str = ', '.join(sorted(q_companies)) if q_companies else '?'
        events = '; '.join(p['title'][:40] for p in qposts[:3])
        if len(qposts) > 3:
            events += f'; +{len(qposts) - 3} más'

        lines.append(f'| {q} | {len(qposts)} | {q_score} | {q_comments} | {company_str} | {events} |')

    lines.append('')

    # === COMPANY TABLE ===
    lines.append('## Érintett Cégek')
    lines.append('')
    lines.append('| Cég | Dátum | Szektor | AI-faktor | Forrás | Link |')
    lines.append('|-----|-------|---------|-----------|--------|------|')

    company_posts = [p for p in strong if p.get('company') or p.get('llm_company')]
    grouped_companies = _group_by_event(company_posts)

    max_companies = 20
    for label, rep, others in grouped_companies[:max_companies]:
        company = rep.get('company') or rep.get('llm_company')
        ai_str = 'igen' if _is_ai_attributed(rep) else '—'
        link = f'[link]({rep["url"]})'
        suffix = f' (+{len(others)} forrás)' if others else ''
        lines.append(
            f'| {company}{suffix} | {rep["date"]} | '
            f'{_eff_sector(rep)} | {ai_str} | {_source_str(rep)} | {link} |'
        )

    remaining = len(grouped_companies) - max_companies
    if remaining > 0:
        lines.append('')
        lines.append(f'*További {remaining} esemény → [Interaktív Dashboard](https://tatargabor.github.io/hu-it-layoffs/report.html#top-posts)*')

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
    for label, group in _event_groups(strong):
        sector = _eff_sector(group[0])
        by_sector[sector] = by_sector.get(sector, 0) + 1

    if by_sector:
        lines.append('**Szektorok szerinti megoszlás (erős jelzések, esemény szinten):**')
        for sector, count in sorted(by_sector.items(), key=lambda x: -x[1]):
            lines.append(f'- {sector}: {count} esemény')
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
        if _is_ai_attributed(p):
            ai_posts_by_year[year]['ai'] += 1

    lines.append('**AI-attribúció évenként:**')
    for year in sorted(ai_posts_by_year.keys()):
        d = ai_posts_by_year[year]
        pct = round(d['ai'] / d['total'] * 100) if d['total'] > 0 else 0
        lines.append(f'- {year}: {d["ai"]}/{d["total"]} poszt ({pct}%)')
    lines.append('')

    lines.append('')
    lines.append('*Részletes adatok (engagement, technológiák, munkakörök, hiring freeze): [Interaktív Dashboard](https://tatargabor.github.io/hu-it-layoffs/report.html)*')
    lines.append('')

    # === METHODOLOGY ===
    lines.append('## Módszertan')
    lines.append('')
    lines.append('### Adatgyűjtés')
    lines.append('A projekt automatizált scraper-rel gyűjt publikus adatokat két forrásból:')
    lines.append('- **Reddit** — r/programmingHungary, r/hungary, r/Layoffs, r/cscareerquestions (poszt szöveg + top 20 komment)')
    lines.append('- **Google News RSS** — magyar nyelvű IT leépítés hírek, teljes cikk szöveggel (a Google News URL-ből kinyert valódi cikk automatikus letöltése)')
    lines.append('')
    lines.append('Keresési lekérdezések magyar és angol nyelven: `elbocsátás`, `leépítés`, `layoff`, `hiring freeze`, `álláskereső`, valamint cégspecifikus keresések (Ericsson, Continental, OTP, Audi, stb.).')
    lines.append('')
    lines.append('### Elemzési pipeline')
    lines.append('1. **Multi-source scraping** — Reddit JSON API + Google News RSS (cikk tartalom kinyeréssel)')
    lines.append('2. **Kulcsszó-alapú elemzés** — relevancia pontozás (0-3), cégfelismerés, AI-attribúció detektálás')
    lines.append('3. **LLM batch triage** — posztcímek batch-szűrése LLM-mel, releváns posztok kiválasztása')
    lines.append('4. **LLM full validáció** — részletes elemzés: kategória, cég, szektor, AI-szerep, technológiák, munkakörök (structured JSON output)')
    lines.append('5. **Report generálás** — Markdown + interaktív HTML dashboard')
    lines.append('')
    lines.append('### LLM validáció')
    lines.append('A pipeline kétszintű LLM szűrést alkalmaz (konfigurálható backend: GitHub Models, Anthropic, Ollama):')
    lines.append('')
    lines.append('**1. Batch triage:** A posztcímeket batch-ekben (~50 cím/kérés) szűri az LLM, kiválasztva a releváns posztokat. Ez csökkenti a full validáció költségét.')
    lines.append('')
    lines.append('**2. Full validáció:** A releváns posztokat egyenként elemzi az LLM, amely meghatározza:')
    lines.append('- Kategória (layoff / freeze / anxiety / other)')
    lines.append('- Érintett cég és iparági szektor (zárt kategórialistából: fintech, automotive, telecom, big tech, IT services, stb.)')
    lines.append('- AI/automatizáció szerepe (direct / factor / concern / none)')
    lines.append('- Confidence score (0.0-1.0)')
    lines.append('- 1 mondatos magyar összefoglaló')
    lines.append('- Érintett technológiák és munkakörök')
    lines.append('')
    lines.append('A szektort az LLM a teljes kontextusból határozza meg — nem csak cégnév alapján, hanem a poszt tartalmából is (pl. "banki IT leépítés" → fintech).')
    lines.append('')
    if llm_stats and llm_stats.get('validated', 0) > 0:
        lines.append(f'Jelen futásban **{llm_stats["validated"]} poszt** validálva **{llm_stats.get("elapsed_seconds", 0):.0f} másodperc** alatt.')
    lines.append('')
    lines.append('### Korlátok')
    lines.append('- Csak publikus források — zárt csoportok, belső kommunikáció nem elérhető')
    lines.append('- A keresések nem garantálják a teljességet')
    lines.append('- LLM validáció nem 100%-os — confidence score jelzi a bizonytalanságot')
    lines.append('')
    lines.append('### Forráskód')
    lines.append('A teljes pipeline nyílt forráskódú: [github.com/tatargabor/hu-it-layoffs](https://github.com/tatargabor/hu-it-layoffs)')
    lines.append('')

    # === TRANSPARENCY STATS ===
    if llm_stats and llm_stats.get('validated', 0) > 0:
        est_input = llm_stats.get('est_input_tokens', 0)
        est_output = llm_stats.get('est_output_tokens', 0)
        manual_hours = llm_stats.get('est_manual_hours', 0)
        elapsed = llm_stats.get('elapsed_seconds', 0)
        backend_name = llm_stats.get('backend_name', 'unknown')

        # Dynamic cost estimation based on backend
        _COST_RATES = {
            'anthropic': (0.80, 4.00, 'Anthropic Haiku'),
            'github': (0.15, 0.60, 'gpt-4o-mini'),
        }
        input_rate, output_rate, rate_label = _COST_RATES.get(backend_name, (0.15, 0.60, backend_name))
        est_cost = est_input / 1_000_000 * input_rate + est_output / 1_000_000 * output_rate

        lines.append('---')
        lines.append('')
        lines.append(f'**LLM validáció:** {llm_stats["validated"]} poszt validálva {elapsed:.0f} másodperc alatt')
        lines.append(f'**Tokenek:** ~{est_input:,} input + ~{est_output:,} output')
        if backend_name in ('ollama', 'openai'):
            lines.append(f'**Költség:** $0.00 (lokális)')
        else:
            lines.append(f'**Becsült költség ({rate_label} áron):** ${est_cost:.3f}')
        lines.append(f'**Kézzel ez ~{manual_hours:.0f} óra munka lett volna**')
        lines.append('')

    lines.append('---')
    lines.append(f'*Összes adat: [data/validated_posts.json](https://github.com/tatargabor/hu-it-layoffs/blob/main/data/validated_posts.json) | [Interaktív Dashboard](https://tatargabor.github.io/hu-it-layoffs/report.html)*')

    report = '\n'.join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f'Report written to {output_path} ({len(lines)} lines)')
    return report


if __name__ == '__main__':
    with open('data/validated_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    generate_report(posts)
