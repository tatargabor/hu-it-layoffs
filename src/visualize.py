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



def generate_html(posts, output_path='data/report.html', llm_stats=None):
    relevant = [p for p in posts if _eff_relevance(p) >= 1]
    strong = [p for p in posts if _eff_relevance(p) >= 2]
    direct = [p for p in posts if _eff_relevance(p) >= 3]

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

    # Stats — recent quarter for primary card
    now = datetime.now()
    q_now = (now.month - 1) // 3 + 1
    cutoff_year = now.year - 1 if q_now <= 1 else now.year
    cutoff_q = (q_now - 1) if q_now > 1 else 4
    cutoff_date = f'{cutoff_year}-{(cutoff_q - 1) * 3 + 1:02d}-01'
    recent_strong = [p for p in strong if p['date'] >= cutoff_date]
    recent_quarter_label = f'{cutoff_date[:4]} Q{cutoff_q}'
    companies = set(p.get('company') or p.get('llm_company') for p in relevant if p.get('company') or p.get('llm_company'))
    ai_count = sum(1 for p in relevant if p.get('ai_attributed'))
    freeze_count = sum(1 for p in relevant if p.get('hiring_freeze_signal'))

    # Source breakdown
    by_source = defaultdict(int)
    for p in relevant:
        src = p.get('source', 'reddit')
        sub = p.get('subreddit', '?')
        label = f'r/{sub}' if src == 'reddit' else src
        by_source[label] += 1

    # Build detailed table rows
    detailed_rows = ''
    for p in all_relevant:
        company = p.get('company') or p.get('llm_company') or '—'
        cat = p.get('category', 'other')
        rel = _eff_relevance(p)
        conf = f'{p["llm_confidence"]:.0%}' if p.get('llm_validated') else '—'
        ai_str = 'igen' if p.get('ai_attributed') else '—'
        title_esc = p['title'][:60].replace('&', '&amp;').replace('<', '&lt;')
        if len(p['title']) > 60:
            title_esc += '...'
        llm_badge = ' &#10003;' if p.get('llm_validated') else ''

        src = p.get('source', 'reddit')
        src_label = f'r/{p.get("subreddit", "?")}' if src == 'reddit' else src

        detailed_rows += f'''<tr>
      <td>{p["date"]}</td>
      <td><a href="{p["url"]}" target="_blank">{title_esc}</a></td>
      <td>{company}</td>
      <td><span class="tag tag-{cat}">{cat}</span></td>
      <td>{src_label}</td>
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
@media (max-width: 768px) {{ .charts {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>magyar.dev/layoffs</h1>
  <div class="sub" style="font-size:1.1em;color:#ccc;margin-bottom:4px">IT Leépítés Radar</div>
  <div class="sub">Reddit (r/programmingHungary, r/hungary) publikus adatok | Generálva: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
  <div class="tagline">Specifikálva OpenSpec-kel, generálva Claude Code-dal</div>
  <div class="share-row">
    <a class="share-btn watch" href="https://github.com/tatargabor/hu-it-layoffs" target="_blank">&#9733; Watch on GitHub</a>
    <a class="share-btn" href="https://www.linkedin.com/sharing/share-offsite/?url=" target="_blank">LinkedIn</a>
    <a class="share-btn" id="copyLink" onclick="navigator.clipboard.writeText(window.location.href).then(()=>{{let b=document.getElementById('copyLink');b.textContent='Copied!';setTimeout(()=>b.textContent='Copy Link',2000)}})">Copy Link</a>
  </div>
</div>

<div class="stats">
  <div class="stat primary"><div class="num">{len(recent_strong)}</div><div class="label">Leépítési jelzés<br><span style="font-size:0.85em;color:#666">{recent_quarter_label} óta</span></div></div>
  <div class="stat"><div class="num">{len(direct)}</div><div class="label">Közvetlen leépítés</div></div>
  <div class="stat"><div class="num">{len(relevant)}</div><div class="label">Releváns poszt</div></div>
  <div class="stat"><div class="num">{len(companies)}</div><div class="label">Érintett cég</div></div>
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
    {"".join(f'''<tr>
      <td>{p["date"]}</td>
      <td><a href="{p["url"]}" target="_blank">{p["title"][:60].replace("&", "&amp;").replace("<", "&lt;")}{"..." if len(p["title"]) > 60 else ""}</a></td>
      <td>{p.get("company") or p.get("llm_company") or "—"}</td>
      <td><span class="tag tag-{p.get("category", "other")}">{p.get("category", "other")}</span></td>
      <td>{"r/" + p.get("subreddit", "?") if p.get("source", "reddit") == "reddit" else p.get("source", "?")}</td>
      <td>{p["score"]}</td>
      <td>{p["num_comments"]}</td>
      <td class="rel-{_eff_relevance(p)}">{"&#9733;" * _eff_relevance(p)}</td>
      <td>{"&#10003;" if p.get("llm_validated") else "—"}</td>
    </tr>''' for p in top_posts)}
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
    <p>Automatizált scraper gyűjt publikus Reddit posztokat az alábbi subredditekről:</p>
    <ul style="margin:8px 0 16px 20px">
      <li><strong>r/programmingHungary</strong> — magyar fejlesztői közösség</li>
      <li><strong>r/hungary</strong> — általános magyar subreddit</li>
      <li><strong>r/Layoffs</strong> — nemzetközi leépítési hírek</li>
      <li><strong>r/cscareerquestions</strong> — IT karrierkérdések</li>
    </ul>
    <p>Keresési lekérdezések magyar és angol nyelven: <em>elbocsátás, leépítés, layoff, hiring freeze, álláskereső</em>, valamint cégspecifikus keresések (Ericsson, Continental, OTP, NNG, Lensa, Microsoft, stb.).</p>

    <h3 style="color:#e94560;margin:16px 0 8px">Elemzési pipeline</h3>
    <ol style="margin:8px 0 16px 20px">
      <li><strong>Scraping</strong> — Reddit JSON API-n keresztül, kommentekkel együtt</li>
      <li><strong>Kulcsszó-alapú elemzés</strong> — relevancia pontozás (0-3), cégfelismerés, AI-attribúció detektálás</li>
      <li><strong>LLM validáció</strong> — minden relevancia &ge; 1 posztot nyelvi modell értékel (structured JSON output)</li>
      <li><strong>Report generálás</strong> — Markdown + interaktív HTML dashboard</li>
    </ol>

    <h3 style="color:#e94560;margin:16px 0 8px">LLM validáció</h3>
    <p>A relevancia &ge; 1 posztokat nyelvi modell validálja: ténylegesen IT leépítésről szól-e, melyik cég érintett, confidence score (0.0-1.0), magyar összefoglaló, érintett technológiák és munkakörök.</p>
    {"<p style='margin-top:8px'><strong>" + str(llm_stats['validated']) + " poszt</strong> validálva <strong>" + f"{llm_stats.get('elapsed_seconds', 0):.0f}" + " másodperc</strong> alatt.</p>" if llm_stats and llm_stats.get('validated', 0) > 0 else ""}

    <h3 style="color:#e94560;margin:16px 0 8px">Korlátok</h3>
    <ul style="margin:8px 0 16px 20px">
      <li>Csak publikus Reddit posztok — zárt csoportok, belső kommunikáció nem elérhető</li>
      <li>A Reddit keresés nem garantálja a teljességet</li>
      <li>LLM validáció nem 100%-os — confidence score jelzi a bizonytalanságot</li>
      <li>Angol nyelvű posztok Budapest/Hungary említéssel nem feltétlenül magyar IT szektorra vonatkoznak</li>
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
