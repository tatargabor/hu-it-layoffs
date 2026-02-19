"""Generate interactive HTML report with Chart.js visualizations."""

import json
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


def _eff_headcount(post):
    if post.get('llm_validated') and post.get('llm_headcount') is not None:
        hc = post['llm_headcount']
        return hc, hc, 'llm'
    return post.get('headcount_min'), post.get('headcount_max'), post.get('headcount_source')


def generate_html(posts, output_path='data/report.html', llm_stats=None):
    relevant = [p for p in posts if _eff_relevance(p) >= 1]
    strong = [p for p in posts if _eff_relevance(p) >= 2]
    direct = [p for p in posts if _eff_relevance(p) >= 3]

    quarters = _all_quarters()

    # Quarter data
    q_direct = defaultdict(int)
    q_strong = defaultdict(int)
    q_indirect = defaultdict(int)
    q_headcount_min = defaultdict(int)
    q_headcount_max = defaultdict(int)
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
        if r >= 2:
            hmin, hmax, _ = _eff_headcount(p)
            q_headcount_min[q] += hmin or 0
            q_headcount_max[q] += hmax or 0
        if p.get('llm_validated'):
            q_llm_validated[q] += 1
        else:
            q_keyword_only[q] += 1

    # Company data
    company_counts = defaultdict(int)
    for p in strong:
        c = p.get('company') or p.get('llm_company')
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
        if p.get('ai_attributed'):
            ai_by_year[year]['ai'] += 1
    ai_years = sorted(ai_by_year.keys())

    # Sector data
    sector_counts = defaultdict(int)
    for p in strong:
        s = p.get('company_sector') or 'ismeretlen'
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

    # Top posts for table
    top_posts = sorted(
        [p for p in relevant if _eff_relevance(p) >= 2],
        key=lambda x: x['created_utc'],
        reverse=True
    )[:30]

    # All relevant posts for detailed table
    all_relevant = sorted(relevant, key=lambda x: x['created_utc'], reverse=True)

    # Stats
    total_min = sum((_eff_headcount(p)[0] or 0) for p in strong)
    total_max = sum((_eff_headcount(p)[1] or 0) for p in strong)
    companies = set(p.get('company') or p.get('llm_company') for p in relevant if p.get('company') or p.get('llm_company'))
    ai_count = sum(1 for p in relevant if p.get('ai_attributed'))
    freeze_count = sum(1 for p in relevant if p.get('hiring_freeze_signal'))

    # Build detailed table rows
    detailed_rows = ''
    for p in all_relevant:
        company = p.get('company') or p.get('llm_company') or '—'
        hmin, hmax, hsrc = _eff_headcount(p)
        if hmin is not None:
            if hsrc == 'explicit' or hsrc == 'llm':
                hc_html = f'<strong>{hmin}</strong>' if hmin == hmax else f'<strong>{hmin}-{hmax}</strong>'
            else:
                hc_html = f'<span style="color:#888">~{hmin}-{hmax}</span>'
        else:
            hc_html = '?'
        cat = p.get('category', 'other')
        rel = _eff_relevance(p)
        conf = f'{p["llm_confidence"]:.0%}' if p.get('llm_validated') else '—'
        ai_str = 'igen' if p.get('ai_attributed') else '—'
        title_esc = p['title'][:60].replace('&', '&amp;').replace('<', '&lt;')
        if len(p['title']) > 60:
            title_esc += '...'
        llm_badge = ' &#10003;' if p.get('llm_validated') else ''

        detailed_rows += f'''<tr>
      <td>{p["date"]}</td>
      <td><a href="{p["url"]}" target="_blank">{title_esc}</a></td>
      <td>{company}</td>
      <td>{hc_html}</td>
      <td><span class="tag tag-{cat}">{cat}</span></td>
      <td>{p["score"]}</td>
      <td>{p["num_comments"]}</td>
      <td class="rel-{rel}">{"&#9733;" * rel}{llm_badge}</td>
      <td>{conf}</td>
      <td>{ai_str}</td>
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
@media (max-width: 768px) {{ .charts {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>magyar.dev/layoffs — IT Leépítés Radar</h1>
  <div class="sub">Reddit (r/programmingHungary, r/hungary) publikus adatok | Generálva: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
</div>

<div class="stats">
  <div class="stat primary"><div class="num">~{total_min:,}–{total_max:,}</div><div class="label">Becsült érintett fő</div></div>
  <div class="stat"><div class="num">{len(direct)}</div><div class="label">Közvetlen leépítés</div></div>
  <div class="stat"><div class="num">{len(relevant)}</div><div class="label">Releváns poszt</div></div>
  <div class="stat"><div class="num">{len(companies)}</div><div class="label">Érintett cég</div></div>
  <div class="stat"><div class="num">{ai_count}</div><div class="label">AI-t említő poszt</div></div>
  <div class="stat"><div class="num">{freeze_count}</div><div class="label">Hiring freeze jelzés</div></div>
</div>

<div class="charts">

<div class="chart-box full">
  <h2>Negyedéves Timeline — Posztok száma</h2>
  <canvas id="timelineChart"></canvas>
</div>

<div class="chart-box full">
  <h2>Becsült Érintett Létszám Negyedévenként</h2>
  <canvas id="headcountChart"></canvas>
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

<div class="table-section">
  <h2>Top Posztok (relevancia >= 2)</h2>
  <table>
    <tr>
      <th>Dátum</th>
      <th>Cím</th>
      <th>Cég</th>
      <th>Kategória</th>
      <th>Score</th>
      <th>Kommentek</th>
      <th>Rel.</th>
    </tr>
    {"".join(f'''<tr>
      <td>{p["date"]}</td>
      <td><a href="{p["url"]}" target="_blank">{p["title"][:60].replace("&", "&amp;").replace("<", "&lt;")}{"..." if len(p["title"]) > 60 else ""}</a></td>
      <td>{p.get("company") or p.get("llm_company") or "—"}</td>
      <td><span class="tag tag-{p.get("category", "other")}">{p.get("category", "other")}</span></td>
      <td>{p["score"]}</td>
      <td>{p["num_comments"]}</td>
      <td class="rel-{_eff_relevance(p)}">{"&#9733;" * _eff_relevance(p)}{" &#10003;" if p.get("llm_validated") else ""}</td>
    </tr>''' for p in top_posts)}
  </table>
</div>

<details>
  <summary>Részletes Táblázat — összes releváns poszt ({len(all_relevant)} db)</summary>
  <table>
    <tr>
      <th>Dátum</th>
      <th>Cím</th>
      <th>Cég</th>
      <th>Létszám</th>
      <th>Kategória</th>
      <th>Score</th>
      <th>Komment</th>
      <th>Rel.</th>
      <th>LLM Conf.</th>
      <th>AI</th>
    </tr>
    {detailed_rows}
  </table>
</details>

<div class="footer">
  Forrás: Reddit publikus JSON API | {len(posts)} poszt feldolgozva | powered by Claude Code &middot; OpenSpec &middot; Agentic
  {"<br>" + f"{llm_stats['validated']} poszt LLM-validálva {llm_stats['elapsed_seconds']:.0f}s alatt | ~{llm_stats['est_input_tokens']:,}+{llm_stats['est_output_tokens']:,} token | Költség: $0.00 (GitHub Models) | Kézzel ez ~{llm_stats['est_manual_hours']:.0f} óra lett volna" if llm_stats and llm_stats.get('validated', 0) > 0 else ""}
</div>

<script>
const quarters = {json.dumps(quarters)};
const qDirect = {json.dumps([q_direct.get(q, 0) for q in quarters])};
const qStrong = {json.dumps([q_strong.get(q, 0) for q in quarters])};
const qIndirect = {json.dumps([q_indirect.get(q, 0) for q in quarters])};
const qFreeze = {json.dumps([freeze_by_q.get(q, 0) for q in quarters])};
const qHcMin = {json.dumps([q_headcount_min.get(q, 0) for q in quarters])};
const qHcMax = {json.dumps([q_headcount_max.get(q, 0) for q in quarters])};
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

// Headcount range chart
new Chart(document.getElementById('headcountChart'), {{
  type: 'bar',
  data: {{
    labels: quarters,
    datasets: [
      {{ label: 'Min becslés', data: qHcMin, backgroundColor: '#e9456088' }},
      {{ label: 'Max becslés', data: qHcMax, backgroundColor: '#e9456033' }}
    ]
  }},
  options: {{
    responsive: true,
    scales: {{ y: {{ beginAtZero: true }} }},
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
