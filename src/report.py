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


def generate_report(posts, output_path='data/report.md', llm_stats=None):
    """Generate full markdown report."""
    relevant = [p for p in posts if _eff_relevance(p) >= 1 and _is_hungarian_relevant(p)]
    strong = [p for p in posts if _eff_relevance(p) >= 2 and _is_hungarian_relevant(p)]
    direct = [p for p in posts if _eff_relevance(p) >= 3 and _is_hungarian_relevant(p)]

    lines = []

    # === SUMMARY ===
    lines.append('# Magyar IT Szektor Leépítések — Kimutatás')
    lines.append('')
    lines.append('**[Interaktív Dashboard](https://tatargabor.github.io/hu-it-layoffs/report.html)** | [GitHub repo](https://github.com/tatargabor/hu-it-layoffs)')
    lines.append('')
    lines.append(f'*Generálva: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Forrás: Reddit publikus adatok*')
    lines.append('')
    lines.append('> **Jogi nyilatkozat:** Ez a kimutatás kizárólag publikusan elérhető Reddit posztok automatizált elemzése. A tartalom harmadik felek által közzétett véleményeket és információkat tükrözi, amelyek pontossága nem ellenőrzött. A kimutatás tájékoztató és kutatási célú, nem minősül tényállításnak egyetlen szervezetről sem. Tartalom eltávolítását a [GitHub Issues](https://github.com/tatargabor/hu-it-layoffs/issues) oldalon lehet kérni.')
    lines.append('>')
    lines.append('> **Disclaimer:** This report is an automated analysis of publicly available Reddit posts. It reflects opinions and information published by third parties, the accuracy of which has not been verified. This report is for informational and research purposes only and does not constitute factual claims about any organization. Content removal requests can be submitted via [GitHub Issues](https://github.com/tatargabor/hu-it-layoffs/issues).')
    lines.append('')

    # Date range
    if relevant:
        dates = sorted(p['date'] for p in relevant)
        lines.append(f'**Időszak:** {dates[0]} – {dates[-1]}')
    lines.append(f'**Összes releváns poszt:** {len(relevant)}')
    lines.append(f'**Közvetlen leépítés riport (relevancia 3):** {len(direct)}')
    lines.append(f'**Erős jelzés (relevancia >= 2):** {len(strong)}')

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
    company_posts.sort(key=lambda x: x['date'], reverse=True)

    for p in company_posts:
        company = p.get('company') or p.get('llm_company')
        ai_str = 'igen' if _is_ai_attributed(p) else '—'
        link = f'[link]({p["url"]})'
        lines.append(
            f'| {company} | {p["date"]} | '
            f'{_eff_sector(p)} | {ai_str} | {_source_str(p)} | {link} |'
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
        sector = _eff_sector(p)
        by_sector[sector] = by_sector.get(sector, 0) + 1

    if by_sector:
        lines.append('**Szektorok szerinti megoszlás (erős jelzések):**')
        for sector, count in sorted(by_sector.items(), key=lambda x: -x[1]):
            lines.append(f'- {sector}: {count} poszt')
        lines.append('')

    # === ENGAGEMENT ===
    lines.append('## Közösségi Engagement')
    lines.append('')

    cat_labels_eng = {
        'layoff': 'Közvetlen leépítés',
        'freeze': 'Hiring freeze / álláspiac',
        'anxiety': 'Karrier aggodalom',
        'other': 'Egyéb',
    }
    eng_cats = defaultdict(lambda: {'posts': 0, 'score': 0, 'comments': 0})
    for p in relevant:
        cat = p.get('llm_category', p.get('category', 'other'))
        eng_cats[cat]['posts'] += 1
        eng_cats[cat]['score'] += p.get('score', 0)
        eng_cats[cat]['comments'] += p.get('num_comments', 0)

    lines.append('| Kategória | Posztok | Össz score | Össz komment | Átl. score | Átl. komment |')
    lines.append('|-----------|---------|------------|--------------|------------|--------------|')
    for cat in ['layoff', 'freeze', 'anxiety']:
        d = eng_cats[cat]
        if d['posts'] > 0:
            label = cat_labels_eng.get(cat, cat)
            avg_s = d['score'] / d['posts']
            avg_c = d['comments'] / d['posts']
            lines.append(f'| {label} | {d["posts"]} | {d["score"]:,} | {d["comments"]:,} | {avg_s:.0f} | {avg_c:.0f} |')
    lines.append('')

    # Top 5 by score
    top_score = sorted(relevant, key=lambda x: x.get('score', 0), reverse=True)[:5]
    lines.append('**Legtöbb reakció (upvote):**')
    for p in top_score:
        lines.append(f'- {p["score"]} upvote — [{p["title"][:60]}]({p["url"]})')
    lines.append('')

    # Top 5 by comments
    top_comments = sorted(relevant, key=lambda x: x.get('num_comments', 0), reverse=True)[:5]
    lines.append('**Legtöbb komment:**')
    for p in top_comments:
        lines.append(f'- {p["num_comments"]} komment — [{p["title"][:60]}]({p["url"]})')
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
        if _is_ai_attributed(p):
            ai_posts_by_year[year]['ai'] += 1

    lines.append('**AI-attribúció évenként:**')
    for year in sorted(ai_posts_by_year.keys()):
        d = ai_posts_by_year[year]
        pct = round(d['ai'] / d['total'] * 100) if d['total'] > 0 else 0
        lines.append(f'- {year}: {d["ai"]}/{d["total"]} poszt ({pct}%)')
    lines.append('')

    _MULTI_SECTORS = {'big tech', 'telecom', 'automotive', 'energy'}
    _STARTUP_SECTORS = {'startup', 'AI/startup'}
    _MID_SECTORS = {'fintech', 'IT services', 'retail tech', 'entertainment'}
    _GOV_SECTORS = {'government', 'finance/gov'}
    company_type = {'multi': 0, 'startup': 0, 'mid': 0, 'gov': 0, 'unknown': 0}
    for p in strong:
        s = _eff_sector(p)
        if s in _MULTI_SECTORS:
            company_type['multi'] += 1
        elif s in _STARTUP_SECTORS:
            company_type['startup'] += 1
        elif s in _MID_SECTORS:
            company_type['mid'] += 1
        elif s in _GOV_SECTORS:
            company_type['gov'] += 1
        else:
            company_type['unknown'] += 1
    lines.append('**Cég típus:**')
    lines.append(f'- Multinacionális / nagyvállalat: {company_type["multi"]} esemény')
    lines.append(f'- Közepes / vegyes: {company_type["mid"]} esemény')
    lines.append(f'- Startup / KKV: {company_type["startup"]} esemény')
    if company_type['gov'] > 0:
        lines.append(f'- Állami: {company_type["gov"]} esemény')
    lines.append(f'- Nem besorolható: {company_type["unknown"]} esemény')
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
    lines.append('| Dátum | Cím | Cég | Kategória | Forrás | Score | Komment | Rel. | LLM Conf. | AI |')
    lines.append('|-------|-----|-----|-----------|--------|-------|---------|------|-----------|----|')

    for p in sorted(relevant, key=lambda x: x['date'], reverse=True):
        company = p.get('company') or p.get('llm_company') or '—'
        cat = p.get('category', 'other')
        rel = _eff_relevance(p)
        conf = f'{p["llm_confidence"]:.0%}' if p.get('llm_validated') else '—'
        ai_str = 'igen' if _is_ai_attributed(p) else '—'
        title_short = p['title'][:50] + ('...' if len(p['title']) > 50 else '')
        lines.append(
            f'| {p["date"]} | [{title_short}]({p["url"]}) | {company} | '
            f'{cat} | {_source_str(p)} | {p["score"]} | {p["num_comments"]} | {rel} | {conf} | {ai_str} |'
        )

    lines.append('')

    # === DATA SOURCES ===
    lines.append('## Források')
    lines.append('')
    # Source breakdown
    by_source = {}
    for p in relevant:
        src_label = _source_str(p)
        by_source[src_label] = by_source.get(src_label, 0) + 1

    source_parts = ', '.join(f'{k}: {v}' for k, v in sorted(by_source.items(), key=lambda x: -x[1]))
    lines.append(f'Összesen {len(relevant)} releváns poszt ({source_parts}):')
    lines.append('')

    for p in sorted(relevant, key=lambda x: x['date'], reverse=True):
        rel_marker = {3: '***', 2: '**', 1: '*'}.get(_eff_relevance(p), '')
        lines.append(
            f'- [{p["date"]}] [{p["title"][:70]}]({p["url"]}) '
            f'(score: {p["score"]}, {p["num_comments"]} komment) {rel_marker}'
        )

    lines.append('')

    # === METHODOLOGY ===
    lines.append('## Módszertan')
    lines.append('')
    lines.append('### Adatgyűjtés')
    lines.append('A projekt automatizált scraper-rel gyűjt publikus Reddit posztokat az alábbi subredditekről:')
    lines.append('- **r/programmingHungary** — magyar fejlesztői közösség')
    lines.append('- **r/hungary** — általános magyar subreddit')
    lines.append('- **r/Layoffs** — nemzetközi leépítési hírek')
    lines.append('- **r/cscareerquestions** — IT karrierkérdések')
    lines.append('')
    lines.append('Keresési lekérdezések magyar és angol nyelven: `elbocsátás`, `leépítés`, `layoff`, `hiring freeze`, `álláskereső`, valamint cégspecifikus keresések (Ericsson, Continental, OTP, NNG, Lensa, Microsoft, stb.).')
    lines.append('')
    lines.append('### Elemzési pipeline')
    lines.append('1. **Scraping** — Reddit JSON API-n keresztül, kommentekkel együtt')
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
    lines.append('- Csak publikus Reddit posztok — zárt csoportok, belső kommunikáció nem elérhető')
    lines.append('- A Reddit keresés nem garantálja a teljességet')
    lines.append('- LLM validáció nem 100%-os — confidence score jelzi a bizonytalanságot')
    lines.append('- Angol nyelvű posztok Budapest/Hungary említéssel nem feltétlenül magyar IT szektorra vonatkoznak')
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
