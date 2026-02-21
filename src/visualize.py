"""Generate interactive HTML report with Chart.js visualizations."""

import json
import re
from datetime import datetime
from collections import defaultdict


def _quarter(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    q = (dt.month - 1) // 3 + 1
    return f'{dt.year} Q{q}'


def _all_quarters(start='2023 Q1', end=None):
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
    if post.get('llm_validated'):
        return post.get('llm_relevance', post.get('relevance', 0))
    return post.get('relevance', 0)


def _is_hungarian_relevant(post):
    """Check if post has Hungarian relevance (not 'none'). Posts without the field are assumed relevant."""
    return post.get('llm_hungarian_relevance', 'direct') != 'none'


_IT_SECTORS = {'fintech', 'big tech', 'IT services', 'telecom', 'startup', 'general IT', 'retail tech',
               'gaming tech', 'travel tech'}
_IT_ROLE_KEYWORDS = {'fejlesztő', 'programozó', 'informatikus', 'szoftver', 'devops', 'qa',
                     'developer', 'engineer', 'software', 'backend', 'frontend',
                     'machine learning', 'mesterséges intelligencia'}
_IT_ROLE_KEYWORDS_WB = re.compile(r'\b(?:ai|ml|IT|data)\b', re.IGNORECASE)


def _eff_category(post):
    """Effective category: llm_category if validated, else category field, else 'other'."""
    if post.get('llm_validated') and post.get('llm_category'):
        return post['llm_category']
    return post.get('category', 'other')


def _is_it_relevant(post):
    """Filter out non-IT sector layoffs unless IT roles/technologies are mentioned."""
    sector = _eff_sector(post)
    if sector in _IT_SECTORS:
        return True
    roles = post.get('llm_roles', [])
    techs = post.get('llm_technologies', [])
    summary = post.get('llm_summary', '')
    text = ' '.join(roles + techs) + ' ' + summary
    lower = text.lower()
    return any(kw in lower for kw in _IT_ROLE_KEYWORDS) or bool(_IT_ROLE_KEYWORDS_WB.search(text))


def _count_events(posts):
    """Count unique events. Posts with same event_label count as 1."""
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
    """Group posts by event_label. Returns list of (label, [posts])."""
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
        sector = post['llm_sector']
        if isinstance(sector, list):
            return sector[0] if sector else 'ismeretlen'
        return sector
    return post.get('company_sector') or 'ismeretlen'


_GENERIC_COMPANY_PATTERNS = ['nagyobb', 'kisebb', 'egy cég', 'élelmiszerlánc', 'nem nevezett']


def _is_named_company(name):
    """Filter out generic/unnamed company references from stats."""
    if not name:
        return False
    if isinstance(name, list):
        name = name[0] if name else ''
    if not name:
        return False
    lower = name.lower()
    return not any(p in lower for p in _GENERIC_COMPANY_PATTERNS)


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
        # Sort: Reddit first, then by relevance desc, then by date desc
        group_posts.sort(key=lambda x: (
            0 if x.get('source') == 'reddit' else 1,
            -_eff_relevance(x),
            -x.get('created_utc', 0),
        ))
        rep = group_posts[0]
        others = group_posts[1:]
        result.append((label, rep, others))

    # Sort all groups by representative date desc
    result.sort(key=lambda x: x[1].get('created_utc', 0), reverse=True)
    return result


def generate_html(posts, output_path='data/report.html', llm_stats=None):
    relevant = [p for p in posts if _eff_relevance(p) >= 1 and _is_hungarian_relevant(p) and _is_it_relevant(p)]
    strong = [p for p in posts if _eff_relevance(p) >= 2 and _is_hungarian_relevant(p) and _is_it_relevant(p) and _eff_category(p) != 'other']
    direct = [p for p in posts if _eff_relevance(p) >= 3 and _is_hungarian_relevant(p)]

    quarters = _all_quarters()

    # Quarter data
    q_direct = defaultdict(int)
    q_strong = defaultdict(int)
    q_indirect = defaultdict(int)
    q_llm_validated = defaultdict(int)
    q_keyword_only = defaultdict(int)

    for p in relevant:
        q = _quarter(p['date'])
        if q not in quarters:
            continue
        r = _eff_relevance(p)
        if r == 3:
            q_direct[q] += 1
        elif r == 2:
            q_strong[q] += 1
        elif r == 1:
            q_indirect[q] += 1
        if p.get('llm_validated'):
            q_llm_validated[q] += 1
        else:
            q_keyword_only[q] += 1

    # Company data (event-level: same event_label = 1 count)
    company_counts = defaultdict(int)
    for label, group in _event_groups(strong):
        c = group[0].get('company') or group[0].get('llm_company')
        if c:
            company_counts[c] += 1

    top_companies = sorted(company_counts.items(), key=lambda x: -x[1])

    # Category data
    cat_counts = defaultdict(int)
    for p in relevant:
        cat_counts[p.get('category', 'other')] += 1

    # AI trend by year
    ai_by_year = defaultdict(lambda: {'total': 0, 'ai': 0})
    for p in relevant:
        year = p['date'][:4]
        ai_by_year[year]['total'] += 1
        if _is_ai_attributed(p):
            ai_by_year[year]['ai'] += 1
    ai_years = sorted(ai_by_year.keys())

    # Sector data (event-level)
    sector_counts = defaultdict(int)
    for label, group in _event_groups(strong):
        s = _eff_sector(group[0])
        sector_counts[s] += 1

    # Hiring freeze timeline
    freeze_by_q = defaultdict(int)
    for p in relevant:
        if p.get('hiring_freeze_signal'):
            q = _quarter(p['date'])
            if q in quarters:
                freeze_by_q[q] += 1

    # Technologies & roles from LLM
    tech_counts = defaultdict(int)
    role_counts = defaultdict(int)
    for p in relevant:
        if p.get('llm_validated'):
            for t in p.get('llm_technologies', []):
                tech_counts[t] += 1
            for r in p.get('llm_roles', []):
                role_counts[r] += 1

    top_techs = sorted(tech_counts.items(), key=lambda x: -x[1])[:15]
    top_roles = sorted(role_counts.items(), key=lambda x: -x[1])[:10]
    has_llm_data = any(p.get('llm_validated') for p in relevant)

    # Top posts for table (exclude category='other' — career advice, offtopic)
    top_posts = sorted(
        [p for p in relevant if _eff_relevance(p) >= 2 and _eff_category(p) != 'other'],
        key=lambda x: x['created_utc'],
        reverse=True
    )[:30]

    # All relevant posts for detailed table
    all_relevant = sorted(relevant, key=lambda x: x['created_utc'], reverse=True)

    # Stats — recent quarter for primary card
    now = datetime.now()
    q_now = (now.month - 1) // 3 + 1
    cutoff_year = now.year - 1 if q_now <= 1 else now.year
    cutoff_q = (q_now - 1) if q_now > 1 else 4
    cutoff_date = f'{cutoff_year}-{(cutoff_q - 1) * 3 + 1:02d}-01'
    recent_strong = [p for p in strong if p['date'] >= cutoff_date]
    recent_quarter_label = f'{cutoff_date[:4]} Q{cutoff_q}'
    companies = set(c for p in relevant for c in [p.get('company') or p.get('llm_company')] if _is_named_company(c))
    ai_count = sum(1 for p in relevant if _is_ai_attributed(p))
    freeze_count = sum(1 for p in relevant if p.get('hiring_freeze_signal'))

    # Engagement data
    total_score = sum(p.get('score', 0) for p in relevant)
    total_comments = sum(p.get('num_comments', 0) for p in relevant)

    eng_cats = defaultdict(lambda: {'posts': 0, 'score': 0, 'comments': 0})
    for p in relevant:
        cat = p.get('llm_category', p.get('category', 'other'))
        eng_cats[cat]['posts'] += 1
        eng_cats[cat]['score'] += p.get('score', 0)
        eng_cats[cat]['comments'] += p.get('num_comments', 0)

    top_by_score = sorted(relevant, key=lambda x: x.get('score', 0), reverse=True)[:5]
    top_by_comments = sorted(relevant, key=lambda x: x.get('num_comments', 0), reverse=True)[:5]

    # Source breakdown
    by_source = defaultdict(int)
    for p in relevant:
        src = p.get('source', 'reddit')
        sub = p.get('subreddit', '?')
        label = f'r/{sub}' if src == 'reddit' else p.get('news_source', src) if src == 'google-news' else src
        by_source[label] += 1

    # Build grouped table rows
    def _src_label(p):
        src = p.get('source', 'reddit')
        if src == 'reddit':
            return f'r/{p.get("subreddit", "?")}'
        if src == 'google-news':
            return p.get('news_source', src)
        return src

    def _reddit_ref_html(others, rep):
        """Return Reddit cross-reference link if group has a Reddit post (and rep is not Reddit)."""
        if rep.get('source') == 'reddit':
            return ''
        for o in others:
            if o.get('source') == 'reddit':
                return f' <a class="reddit-ref" href="{o["url"]}" target="_blank" title="Reddit diskurzus">r/</a>'
        return ''

    # Group all relevant posts for detailed table
    grouped_all = _group_by_event(all_relevant)

    detailed_rows = ''
    for label, rep, others in grouped_all:
        company = rep.get('company') or rep.get('llm_company') or '—'
        cat = rep.get('category', 'other')
        rel = _eff_relevance(rep)
        conf = f'{rep["llm_confidence"]:.0%}' if rep.get('llm_validated') else '—'
        ai_str = 'igen' if _is_ai_attributed(rep) else '—'
        title_esc = rep['title'][:60].replace('&', '&amp;').replace('<', '&lt;')
        if len(rep['title']) > 60:
            title_esc += '...'
        llm_badge = ' &#10003;' if rep.get('llm_validated') else ''
        badge = f'<span class="badge">{len(others)+1} forrás</span>' if others else ''
        reddit_ref = _reddit_ref_html(others, rep) if others else ''

        if not others:
            detailed_rows += f'''<tr>
      <td>{rep["date"]}</td>
      <td><a href="{rep["url"]}" target="_blank">{title_esc}</a></td>
      <td>{company}</td>
      <td><span class="tag tag-{cat}">{cat}</span></td>
      <td>{_src_label(rep)}</td>
      <td>{rep["score"]}</td>
      <td>{rep["num_comments"]}</td>
      <td class="rel-{rel}">{"&#9733;" * rel}{llm_badge}</td>
      <td>{conf}</td>
      <td>{ai_str}</td>
    </tr>'''
        else:
            sub_html = ''
            for o in others:
                o_title = o['title'][:55].replace('&', '&amp;').replace('<', '&lt;')
                if len(o['title']) > 55:
                    o_title += '...'
                sub_html += f'<tr class="sub-row"><td>{o["date"]}</td><td colspan="9"><a href="{o["url"]}" target="_blank">{o_title}</a> — {_src_label(o)}</td></tr>'

            detailed_rows += f'''<tr class="event-group"><td>{rep["date"]}</td>
      <td><details><summary><a href="{rep["url"]}" target="_blank">{title_esc}</a>{badge}{reddit_ref}</summary>{sub_html}</details></td>
      <td>{company}</td>
      <td><span class="tag tag-{cat}">{cat}</span></td>
      <td>{_src_label(rep)}</td>
      <td>{rep["score"]}</td>
      <td>{rep["num_comments"]}</td>
      <td class="rel-{rel}">{"&#9733;" * rel}{llm_badge}</td>
      <td>{conf}</td>
      <td>{ai_str}</td>
    </tr>'''

    # Group top posts too
    top_posts_strong = [p for p in relevant if _eff_relevance(p) >= 2 and _eff_category(p) != 'other']
    grouped_top = _group_by_event(top_posts_strong)[:30]

    top_posts_rows = ''
    for label, rep, others in grouped_top:
        title_esc = rep['title'][:60].replace('&', '&amp;').replace('<', '&lt;')
        if len(rep['title']) > 60:
            title_esc += '...'
        badge = f'<span class="badge">{len(others)+1} forrás</span>' if others else ''
        reddit_ref = _reddit_ref_html(others, rep) if others else ''

        if not others:
            top_posts_rows += f'''<tr>
      <td>{rep["date"]}</td>
      <td><a href="{rep["url"]}" target="_blank">{title_esc}</a></td>
      <td>{rep.get("company") or rep.get("llm_company") or "—"}</td>
      <td><span class="tag tag-{rep.get("category", "other")}">{rep.get("category", "other")}</span></td>
      <td>{_src_label(rep)}</td>
      <td>{rep["score"]}</td>
      <td>{rep["num_comments"]}</td>
      <td class="rel-{_eff_relevance(rep)}">{"&#9733;" * _eff_relevance(rep)}</td>
      <td>{"&#10003;" if rep.get("llm_validated") else "—"}</td>
    </tr>'''
        else:
            sub_html = ''
            for o in others:
                o_title = o['title'][:55].replace('&', '&amp;').replace('<', '&lt;')
                if len(o['title']) > 55:
                    o_title += '...'
                sub_html += f'<tr class="sub-row"><td>{o["date"]}</td><td colspan="8"><a href="{o["url"]}" target="_blank">{o_title}</a> — {_src_label(o)}</td></tr>'

            top_posts_rows += f'''<tr class="event-group"><td>{rep["date"]}</td>
      <td><details><summary><a href="{rep["url"]}" target="_blank">{title_esc}</a>{badge}{reddit_ref}</summary>{sub_html}</details></td>
      <td>{rep.get("company") or rep.get("llm_company") or "—"}</td>
      <td><span class="tag tag-{rep.get("category", "other")}">{rep.get("category", "other")}</span></td>
      <td>{_src_label(rep)}</td>
      <td>{rep["score"]}</td>
      <td>{rep["num_comments"]}</td>
      <td class="rel-{_eff_relevance(rep)}">{"&#9733;" * _eff_relevance(rep)}</td>
      <td>{"&#10003;" if rep.get("llm_validated") else "—"}</td>
    </tr>'''

    # Tech/roles chart sections
    tech_chart_html = ''
    tech_chart_js = ''
    if has_llm_data and top_techs:
        tech_chart_html = '''
<div class="chart-box">
  <h2>Érintett Technológiák (top 15)</h2>
  <canvas id="techChart"></canvas>
</div>'''
        tech_chart_js = f'''
new Chart(document.getElementById('techChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([t[0] for t in top_techs])},
    datasets: [{{ label: 'Posztok', data: {json.dumps([t[1] for t in top_techs])}, backgroundColor: '#4ecdc4' }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});'''

    roles_chart_html = ''
    roles_chart_js = ''
    if has_llm_data and top_roles:
        roles_chart_html = '''
<div class="chart-box">
  <h2>Érintett Munkakörök (top 10)</h2>
  <canvas id="rolesChart"></canvas>
</div>'''
        roles_chart_js = f'''
new Chart(document.getElementById('rolesChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([r[0] for r in top_roles])},
    datasets: [{{ label: 'Posztok', data: {json.dumps([r[1] for r in top_roles])}, backgroundColor: '#f9a826' }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});'''

    html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>magyar.dev/layoffs — IT Leépítés Radar</title>
<meta property="og:title" content="magyar.dev/layoffs — IT Leépítés Radar">
<meta property="og:description" content="{len(companies)} érintett cég, {len(recent_strong)} jelzés {recent_quarter_label} óta, {len(relevant)} poszt alapján">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="magyar.dev/layoffs — IT Leépítés Radar">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #0f0f0f; color: #e0e0e0; }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 40px 20px; text-align: center; border-bottom: 2px solid #e94560; }}
.header h1 {{ font-size: 2em; color: #fff; margin-bottom: 8px; }}
.header .sub {{ color: #888; font-size: 0.9em; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; padding: 24px; max-width: 1200px; margin: 0 auto; }}
.stat {{ background: #1a1a2e; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #2a2a4a; }}
.stat .num {{ font-size: 2em; font-weight: 700; color: #e94560; }}
.stat.primary {{ border-color: #e94560; }}
.stat.primary .num {{ font-size: 2.5em; }}
.stat .label {{ font-size: 0.85em; color: #888; margin-top: 4px; }}
.charts {{ max-width: 1200px; margin: 0 auto; padding: 24px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.chart-box {{ background: #1a1a2e; border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a; }}
.chart-box.full {{ grid-column: 1 / -1; }}
.chart-box h2 {{ font-size: 1.1em; color: #ccc; margin-bottom: 12px; }}
canvas {{ max-height: 350px; }}
.table-section {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
.table-section h2 {{ font-size: 1.2em; color: #ccc; margin-bottom: 12px; }}
table {{ width: 100%; border-collapse: collapse; background: #1a1a2e; border-radius: 12px; overflow: hidden; }}
th {{ background: #16213e; color: #e94560; padding: 12px 8px; text-align: left; font-size: 0.85em; font-weight: 600; }}
td {{ padding: 10px 8px; border-bottom: 1px solid #2a2a4a; font-size: 0.85em; }}
tr:hover {{ background: #16213e; }}
a {{ color: #4ecdc4; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.rel-3 {{ color: #e94560; font-weight: 700; }}
.rel-2 {{ color: #f9a826; }}
.rel-1 {{ color: #888; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }}
.tag-layoff {{ background: #e9456033; color: #e94560; }}
.tag-freeze {{ background: #4ecdc433; color: #4ecdc4; }}
.tag-anxiety {{ background: #f9a82633; color: #f9a826; }}
.tag-other {{ background: #88888833; color: #888; }}
details {{ max-width: 1200px; margin: 0 auto; padding: 0 24px 24px; }}
details summary {{ cursor: pointer; font-size: 1.2em; color: #ccc; padding: 12px 0; }}
details summary:hover {{ color: #fff; }}
.footer {{ text-align: center; padding: 40px; color: #555; font-size: 0.8em; }}
.share-row {{ display: flex; gap: 8px; justify-content: center; margin-top: 16px; flex-wrap: wrap; }}
.share-btn {{ display: inline-block; padding: 6px 14px; border-radius: 6px; font-size: 0.8em; color: #fff; text-decoration: none; cursor: pointer; border: 1px solid #2a2a4a; background: #1a1a2e; transition: background 0.2s; }}
.share-btn:hover {{ background: #2a2a4a; text-decoration: none; }}
.share-btn.watch {{ border-color: #e94560; }}
.tagline {{ color: #666; font-size: 0.8em; margin-top: 8px; font-style: italic; }}
.section-anchor {{ color: #555; text-decoration: none; font-size: 0.8em; margin-left: 6px; opacity: 0; transition: opacity 0.2s; }}
.chart-box:hover .section-anchor, .table-section:hover .section-anchor, details:hover .section-anchor {{ opacity: 1; }}
.section-anchor:hover {{ color: #e94560; }}
.event-group summary {{ cursor: pointer; list-style: none; }}
.event-group summary::-webkit-details-marker {{ display: none; }}
.event-group .badge {{ display: inline-block; background: #2a2a4a; color: #4ecdc4; padding: 1px 6px; border-radius: 3px; font-size: 0.7em; margin-left: 6px; vertical-align: middle; }}
.event-group .sub-row td {{ padding-left: 24px; color: #888; font-size: 0.8em; border-bottom: 1px solid #1a1a2e; }}
.event-group .sub-row:hover {{ background: #12122a; }}
.reddit-ref {{ display: inline-block; background: #ff450033; color: #ff4500; padding: 1px 5px; border-radius: 3px; font-size: 0.65em; font-weight: 600; margin-left: 4px; vertical-align: middle; text-decoration: none; }}
.reddit-ref:hover {{ background: #ff450055; text-decoration: none; }}
@media (max-width: 768px) {{ .charts {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>magyar.dev/layoffs</h1>
  <div class="sub" style="font-size:1.1em;color:#ccc;margin-bottom:4px">IT Leépítés Radar</div>
  <div class="sub">Reddit + Google News publikus adatok | Generálva: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
  <div class="tagline">Specifikálva OpenSpec-kel, generálva Claude Code-dal</div>
  <div class="share-row">
    <a class="share-btn watch" href="https://github.com/tatargabor/hu-it-layoffs" target="_blank">&#9733; Watch on GitHub</a>
    <a class="share-btn" href="https://www.linkedin.com/sharing/share-offsite/?url=" target="_blank">LinkedIn</a>
    <a class="share-btn" id="copyLink" onclick="navigator.clipboard.writeText(window.location.href).then(()=>{{let b=document.getElementById('copyLink');b.textContent='Copied!';setTimeout(()=>b.textContent='Copy Link',2000)}})">Copy Link</a>
  </div>
</div>

<div style="max-width:1200px;margin:0 auto;padding:12px 24px">
  <div style="background:#1a1a2e;border:1px solid #2a2a4a;border-radius:8px;padding:12px 16px;font-size:0.75em;color:#666;line-height:1.5">
    <strong style="color:#888">Jogi nyilatkozat / Disclaimer:</strong> Ez a kimutatás publikusan elérhető posztok és hírek automatizált elemzése. A tartalom harmadik felek véleményeit tükrözi, pontossága nem ellenőrzött. Tájékoztató és kutatási célú, nem minősül tényállításnak. /
    This report is an automated analysis of publicly available posts and news articles reflecting third-party opinions. Accuracy is not verified. For informational purposes only.
    <a href="https://github.com/tatargabor/hu-it-layoffs/issues" target="_blank" style="color:#4ecdc4">Eltávolítás kérése / Request removal</a>
  </div>
</div>

<div class="stats">
  <div class="stat primary"><div class="num">{len(recent_strong)}</div><div class="label">Leépítési jelzés<br><span style="font-size:0.85em;color:#666">{recent_quarter_label} óta</span></div></div>
  <div class="stat"><div class="num">{len(direct)}</div><div class="label">Közvetlen leépítés</div></div>
  <div class="stat"><div class="num">{len(relevant)}</div><div class="label">Releváns poszt</div></div>
  <div class="stat"><div class="num">{len(companies)}</div><div class="label">Érintett cég</div></div>
  <div class="stat"><div class="num">{total_score:,}</div><div class="label">Upvote</div></div>
  <div class="stat"><div class="num">{total_comments:,}</div><div class="label">Komment</div></div>
  <div class="stat"><div class="num">{ai_count}</div><div class="label">AI-t említő poszt</div></div>
  <div class="stat"><div class="num">{freeze_count}</div><div class="label">Hiring freeze jelzés</div></div>
</div>

<div class="charts">

<div class="chart-box full" id="timeline">
  <h2>Negyedéves Timeline — Posztok száma <a class="section-anchor" href="#timeline" onclick="navigator.clipboard.writeText(window.location.origin+window.location.pathname+'#timeline')">&#128279;</a></h2>
  <canvas id="timelineChart"></canvas>
</div>

<div class="chart-box">
  <h2>Érintett Cégek</h2>
  <canvas id="companyChart"></canvas>
</div>

<div class="chart-box">
  <h2>Szektorok</h2>
  <canvas id="sectorChart"></canvas>
</div>

<div class="chart-box">
  <h2>Kategóriák</h2>
  <canvas id="categoryChart"></canvas>
</div>

<div class="chart-box">
  <h2>AI Attribúció Trendje</h2>
  <canvas id="aiChart"></canvas>
</div>

{tech_chart_html}

{roles_chart_html}

</div>

<div class="table-section" id="engagement">
  <h2>Közösségi Engagement <a class="section-anchor" href="#engagement" onclick="navigator.clipboard.writeText(window.location.origin+window.location.pathname+'#engagement')">&#128279;</a></h2>
  <table>
    <tr><th>Kategória</th><th>Posztok</th><th>Össz score</th><th>Össz komment</th><th>Átl. score</th><th>Átl. komment</th></tr>
    {"".join(f'<tr><td><span class="tag tag-{cat}">{cat}</span></td><td>{eng_cats[cat]["posts"]}</td><td>{eng_cats[cat]["score"]:,}</td><td>{eng_cats[cat]["comments"]:,}</td><td>{eng_cats[cat]["score"]//max(eng_cats[cat]["posts"],1)}</td><td>{eng_cats[cat]["comments"]//max(eng_cats[cat]["posts"],1)}</td></tr>' for cat in ['layoff', 'freeze', 'anxiety'] if eng_cats[cat]['posts'] > 0)}
  </table>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:16px">
    <div>
      <h3 style="color:#ccc;font-size:0.95em;margin-bottom:8px">Legtöbb upvote</h3>
      <table>
        <tr><th>Score</th><th>Poszt</th></tr>
        {"".join(f'<tr><td style="color:#e94560;font-weight:700">{p["score"]}</td><td><a href="{p["url"]}" target="_blank">{p["title"][:55].replace("&","&amp;").replace("<","&lt;")}{"..." if len(p["title"])>55 else ""}</a></td></tr>' for p in top_by_score)}
      </table>
    </div>
    <div>
      <h3 style="color:#ccc;font-size:0.95em;margin-bottom:8px">Legtöbb komment</h3>
      <table>
        <tr><th>Komment</th><th>Poszt</th></tr>
        {"".join(f'<tr><td style="color:#4ecdc4;font-weight:700">{p["num_comments"]}</td><td><a href="{p["url"]}" target="_blank">{p["title"][:55].replace("&","&amp;").replace("<","&lt;")}{"..." if len(p["title"])>55 else ""}</a></td></tr>' for p in top_by_comments)}
      </table>
    </div>
  </div>
</div>

<div class="table-section" id="top-posts">
  <h2>Top Posztok (relevancia >= 2) <a class="section-anchor" href="#top-posts" onclick="navigator.clipboard.writeText(window.location.origin+window.location.pathname+'#top-posts')">&#128279;</a></h2>
  <table>
    <tr>
      <th>Dátum</th>
      <th>Cím</th>
      <th>Cég</th>
      <th>Kategória</th>
      <th>Forrás</th>
      <th>Score</th>
      <th>Kommentek</th>
      <th>Rel.</th>
      <th>LLM</th>
    </tr>
    {top_posts_rows}
  </table>
</div>

<details id="detailed">
  <summary>Részletes Táblázat — összes releváns poszt ({len(all_relevant)} db) <a class="section-anchor" href="#detailed" onclick="navigator.clipboard.writeText(window.location.origin+window.location.pathname+'#detailed')">&#128279;</a></summary>
  <table>
    <tr>
      <th>Dátum</th>
      <th>Cím</th>
      <th>Cég</th>
      <th>Kategória</th>
      <th>Forrás</th>
      <th>Score</th>
      <th>Komment</th>
      <th>Rel.</th>
      <th>LLM Conf.</th>
      <th>AI</th>
    </tr>
    {detailed_rows}
  </table>
</details>

<details id="methodology" style="margin-top:8px">
  <summary>Módszertan <a class="section-anchor" href="#methodology" onclick="navigator.clipboard.writeText(window.location.origin+window.location.pathname+'#methodology')">&#128279;</a></summary>
  <div style="background:#1a1a2e;border-radius:12px;padding:20px;border:1px solid #2a2a4a;margin-top:12px;line-height:1.7">
    <h3 style="color:#e94560;margin-bottom:8px">Adatgyűjtés</h3>
    <p>Automatizált scraper gyűjt publikus adatokat két forrásból:</p>
    <ul style="margin:8px 0 16px 20px">
      <li><strong>Reddit</strong> — r/programmingHungary, r/hungary, r/Layoffs, r/cscareerquestions (poszt szöveg + top 20 komment)</li>
      <li><strong>Google News RSS</strong> — magyar nyelvű IT leépítés hírek, teljes cikk szöveggel (URL dekódolás + tartalom kinyerés)</li>
    </ul>
    <p style="margin-top:8px">Keresési lekérdezések magyar és angol nyelven: <em>elbocsátás, leépítés, layoff, hiring freeze, álláskereső</em>, valamint cégspecifikus keresések (Ericsson, Continental, OTP, Audi, stb.).</p>

    <h3 style="color:#e94560;margin:16px 0 8px">Elemzési pipeline</h3>
    <ol style="margin:8px 0 16px 20px">
      <li><strong>Multi-source scraping</strong> — Reddit JSON API + Google News RSS (cikk tartalom kinyeréssel)</li>
      <li><strong>Kulcsszó-alapú elemzés</strong> — relevancia pontozás (0-3), cégfelismerés, AI-attribúció detektálás</li>
      <li><strong>LLM validáció</strong> — minden relevancia &ge; 1 posztot nyelvi modell értékel (structured JSON output)</li>
      <li><strong>Report generálás</strong> — Markdown + interaktív HTML dashboard</li>
    </ol>

    <h3 style="color:#e94560;margin:16px 0 8px">LLM validáció</h3>
    <p>A relevancia &ge; 1 posztokat nyelvi modell validálja: ténylegesen IT leépítésről szól-e, melyik cég érintett, confidence score (0.0-1.0), magyar összefoglaló, érintett technológiák és munkakörök.</p>
    {"<p style='margin-top:8px'><strong>" + str(llm_stats['validated']) + " poszt</strong> validálva <strong>" + f"{llm_stats.get('elapsed_seconds', 0):.0f}" + " másodperc</strong> alatt.</p>" if llm_stats and llm_stats.get('validated', 0) > 0 else ""}

    <h3 style="color:#e94560;margin:16px 0 8px">Korlátok</h3>
    <ul style="margin:8px 0 16px 20px">
      <li>Csak publikus források — zárt csoportok, belső kommunikáció nem elérhető</li>
      <li>A keresések nem garantálják a teljességet</li>
      <li>LLM validáció nem 100%-os — confidence score jelzi a bizonytalanságot</li>
    </ul>

    <p><strong>Forráskód:</strong> <a href="https://github.com/tatargabor/hu-it-layoffs" target="_blank">github.com/tatargabor/hu-it-layoffs</a></p>
  </div>
</details>

<div class="footer">
  Források: {", ".join(f"{k} ({v})" for k, v in sorted(by_source.items(), key=lambda x: -x[1]))} | {len(posts)} poszt feldolgozva | powered by Claude Code &middot; OpenSpec &middot; Agentic
  {"<br>" + f"{llm_stats['validated']} poszt LLM-validálva {llm_stats['elapsed_seconds']:.0f}s alatt | ~{llm_stats['est_input_tokens']:,}+{llm_stats['est_output_tokens']:,} token | Költség: $0.00 (GitHub Models) | Kézzel ez ~{llm_stats['est_manual_hours']:.0f} óra lett volna" if llm_stats and llm_stats.get('validated', 0) > 0 else ""}
</div>

<script>
const quarters = {json.dumps(quarters)};
const qDirect = {json.dumps([q_direct.get(q, 0) for q in quarters])};
const qStrong = {json.dumps([q_strong.get(q, 0) for q in quarters])};
const qIndirect = {json.dumps([q_indirect.get(q, 0) for q in quarters])};
const qFreeze = {json.dumps([freeze_by_q.get(q, 0) for q in quarters])};
const qLlmValidated = {json.dumps([q_llm_validated.get(q, 0) for q in quarters])};
const qKeywordOnly = {json.dumps([q_keyword_only.get(q, 0) for q in quarters])};

Chart.defaults.color = '#888';
Chart.defaults.borderColor = '#2a2a4a';

// Timeline stacked bar with LLM opacity
new Chart(document.getElementById('timelineChart'), {{
  type: 'bar',
  data: {{
    labels: quarters,
    datasets: [
      {{ label: 'Közvetlen leépítés (3)', data: qDirect, backgroundColor: '#e94560' }},
      {{ label: 'Erős jelzés (2)', data: qStrong, backgroundColor: '#f9a826' }},
      {{ label: 'Közvetett (1)', data: qIndirect, backgroundColor: '#4ecdc4' }},
      {{ label: 'Hiring freeze', data: qFreeze, backgroundColor: '#9b59b6', type: 'line', borderColor: '#9b59b6', fill: false, tension: 0.3, yAxisID: 'y' }}
    ]
  }},
  options: {{
    responsive: true,
    scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, beginAtZero: true }} }},
    plugins: {{ legend: {{ position: 'bottom' }} }}
  }}
}});

// Company bar chart
new Chart(document.getElementById('companyChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([c[0] for c in top_companies])},
    datasets: [{{ label: 'Posztok', data: {json.dumps([c[1] for c in top_companies])}, backgroundColor: '#e94560' }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});

// Sector doughnut
new Chart(document.getElementById('sectorChart'), {{
  type: 'doughnut',
  data: {{
    labels: {json.dumps(list(sector_counts.keys()))},
    datasets: [{{ data: {json.dumps(list(sector_counts.values()))}, backgroundColor: ['#e94560','#f9a826','#4ecdc4','#9b59b6','#3498db','#2ecc71','#e67e22','#1abc9c','#e74c3c','#95a5a6','#34495e'] }}]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 12 }} }} }} }}
}});

// Category doughnut
new Chart(document.getElementById('categoryChart'), {{
  type: 'doughnut',
  data: {{
    labels: {json.dumps([{'layoff': 'Közvetlen leépítés', 'freeze': 'Hiring freeze', 'anxiety': 'Karrier aggodalom', 'other': 'Egyéb'}.get(k, k) for k in cat_counts.keys()])},
    datasets: [{{ data: {json.dumps(list(cat_counts.values()))}, backgroundColor: ['#e94560','#4ecdc4','#f9a826','#888'] }}]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 12 }} }} }} }}
}});

// AI trend
new Chart(document.getElementById('aiChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(ai_years)},
    datasets: [
      {{ label: 'AI-t említő', data: {json.dumps([ai_by_year[y]['ai'] for y in ai_years])}, backgroundColor: '#e94560' }},
      {{ label: 'Összes releváns', data: {json.dumps([ai_by_year[y]['total'] for y in ai_years])}, backgroundColor: '#2a2a4a' }}
    ]
  }},
  options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }}, plugins: {{ legend: {{ position: 'bottom' }} }} }}
}});

{tech_chart_js}

{roles_chart_js}
</script>

</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'HTML report written to {output_path}')


if __name__ == '__main__':
    with open('data/validated_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    generate_html(posts)
