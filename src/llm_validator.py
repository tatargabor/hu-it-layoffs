"""LLM validator — validates analyzed posts using GitHub Models API or local Ollama."""

import json
import os
import subprocess
import time
import urllib.request
import urllib.error


GITHUB_API_URL = 'https://models.inference.ai.azure.com/chat/completions'
OLLAMA_API_URL = 'http://localhost:11434/v1/chat/completions'
ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'

TRIAGE_SYSTEM_PROMPT = """Te egy magyar IT munkaerőpiaci elemző vagy. A feladatod egy poszt-lista szűrése: jelöld meg melyik posztok RELEVÁNSAK az IT munkaerőpiac szempontjából.

Releváns posztok (BŐVEN szűrj, inkább legyen több mint kevesebb):
- Leépítés, elbocsátás, létszámcsökkentés (bármely szektorban, ha magyarországi)
- Hiring freeze, felvételi stop, álláspiac-romlás
- Nehéz elhelyezkedés, álláskeresési nehézségek az IT-ben
- Karrier-aggodalom, bizonytalanság, kiégés, pályaváltás kérdések
- AI/automatizáció hatása a munkára, munkahelyek megszűnése
- IT munkaerőpiaci kérdések (fizetés, piac helyzete, kereslet/kínálat)
- Cégekről szóló hírek amik a munkaerőpiacot érintik

NEM releváns:
- Technikai kérdések (milyen monitort vegyek, kód hibakeresés)
- Tanulási kérdések amik NEM kapcsolódnak a munkaerőpiachoz
- Általános politika/gazdaság ami NEM érinti közvetlenül a munkaerőpiacot
- Szórakozás, mém, offtopic

Válaszolj JSON formátumban: {"relevant": [1, 5, 12, ...]}
Ahol a számok a releváns posztok SORSZÁMAI (1-től kezdve).

FONTOS: Inkább jelölj relevánsnak egy kétes posztot, mint hogy kihagyd! A következő lépésben részletesen is megvizsgáljuk. Csak JSON-t válaszolj!"""

SYSTEM_PROMPT = """Te egy magyar IT szektorral foglalkozó elemző vagy. A feladatod Reddit posztok kategorizálása az IT munkaerőpiac szempontjából.

Válaszolj JSON formátumban az alábbi sémával:
{
  "is_actual_layoff": true/false,
  "category": "layoff|freeze|anxiety|other",
  "confidence": 0.0-1.0,
  "company": "cégnév vagy null",
  "headcount": szám vagy null,
  "summary": "1 mondatos magyar összefoglaló",
  "technologies": ["technológia1", "technológia2"],
  "roles": ["munkakör1", "munkakör2"],
  "ai_role": "direct|factor|concern|none",
  "ai_context": "1 mondatos magyarázat vagy null"
}

Mezők:
- is_actual_layoff: true ha a poszt konkrét IT leépítésről/elbocsátásról szól
- category: a poszt kategóriája az alábbiak közül:
  - "layoff": Konkrét elbocsátás, leépítés, létszámcsökkentés (pl. "200 embert kirúgtak")
  - "freeze": Hiring freeze, álláspiac-romlás, nehéz elhelyezkedés, felvételi stop (pl. "egy éve nem találok munkát", "nem vesznek fel senkit")
  - "anxiety": Karrier-aggodalom, bizonytalanság, kiégés, pályaváltás kérdések az IT szektorra vonatkozóan (pl. "megéri programozónak tanulni?", "AI elveszi a munkánkat?")
  - "other": Nem kapcsolódik az IT munkaerőpiachoz (általános kérdés, hír, offtopic)
- confidence: mennyire vagy biztos a category besorolásban (0.0-1.0)
- company: az érintett cég neve ha azonosítható, egyébként null
- headcount: becsült érintett létszám ha kiderül a posztból, egyébként null
- summary: 1 mondatos magyar összefoglaló a poszt lényegéről
- technologies: programozási nyelvek, keretrendszerek, eszközök amik a posztban szerepelnek (pl. "Java", "React", "SAP", "Kubernetes"). Üres lista ha nincs ilyen.
- roles: munkakörök, pozíciók amik a posztban szerepelnek (pl. "backend fejlesztő", "DevOps", "QA", "project manager"). Üres lista ha nincs ilyen.
- ai_role: az AI/automatizáció szerepe a posztban:
  - "direct": AI/automatizáció közvetlen oka a leépítésnek/változásnak (pl. "AI-val kiváltották a tesztelőket", "robotizáció miatt szűkítettek")
  - "factor": AI/automatizáció háttér-szerepet játszik (pl. "az AI által megoldott fejlesztések miatt kevesebb ember kell")
  - "concern": AI-val kapcsolatos szorongás, aggodalom (pl. "megéri tanulni, ha AI elveszi a munkát?", "ChatGPT kiváltja a juniorokat")
  - "none": nincs AI/automatizáció vonatkozás
- ai_context: ha ai_role nem "none", 1 mondatos magyar magyarázat az AI szerepéről. Ha ai_role "none", legyen null.

Példák:

Poszt: "Ericsson 200 embert bocsát el Budapesten, főleg firmware és embedded fejlesztők érintettek"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.95, "company": "Ericsson", "headcount": 200, "summary": "Az Ericsson 200 firmware és embedded fejlesztőt bocsát el budapesti irodájából.", "technologies": ["firmware", "embedded"], "roles": ["firmware fejlesztő", "embedded fejlesztő"], "ai_role": "none", "ai_context": null}

Poszt: "Szállás Group közel 70 fejlesztőt bocsát el, az AI által megoldott fejlesztések az indoklás"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.95, "company": "Szállás Group", "headcount": 70, "summary": "A Szállás Group 70 fejlesztőt bocsát el, AI-val indokolva.", "technologies": ["AI"], "roles": ["fejlesztő"], "ai_role": "factor", "ai_context": "A cég az AI-val kiváltott fejlesztésekkel indokolta a leépítést."}

Poszt: "Lassan egy éve nem találok munkát, merre tovább?"
Válasz: {"is_actual_layoff": false, "category": "freeze", "confidence": 0.85, "company": null, "headcount": null, "summary": "A szerző egy éve nem talál IT munkát, az álláspiac beszűkült.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null}

Poszt: "Megéri programozónak tanulni 2025-ben? AI elveszi a munkánkat?"
Válasz: {"is_actual_layoff": false, "category": "anxiety", "confidence": 0.9, "company": null, "headcount": null, "summary": "Karrier-aggodalom az AI hatásáról az IT szektorra.", "technologies": ["AI"], "roles": ["programozó"], "ai_role": "concern", "ai_context": "A szerző az AI munkaerőpiaci hatása miatt aggódik."}

Poszt: "Continental AI Center Budapest leépítés — a divízió áthelyezése az ok"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.9, "company": "Continental", "headcount": null, "summary": "A Continental budapesti AI Center-ben leépítés a divízió áthelyezése miatt.", "technologies": ["AI"], "roles": [], "ai_role": "none", "ai_context": null}

Poszt: "Milyen monitort ajánlotok home office-hoz?"
Válasz: {"is_actual_layoff": false, "category": "other", "confidence": 0.95, "company": null, "headcount": null, "summary": "Monitor vásárlási tanács, nem kapcsolódik a munkaerőpiachoz.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null}

FONTOS: Csak JSON-t válaszolj, semmi mást!"""


def _resolve_backend():
    """Resolve LLM backend config from env vars. Returns dict with url, headers, model, delay."""
    backend = os.environ.get('LLM_BACKEND', 'github').lower()

    if backend == 'ollama':
        model = os.environ.get('LLM_MODEL', 'llama3.1')
        return {
            'name': 'ollama',
            'url': OLLAMA_API_URL,
            'headers': {'Content-Type': 'application/json'},
            'model': model,
            'delay': 0,
        }

    if backend == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        model = os.environ.get('LLM_MODEL', 'claude-haiku-4-5-20241022')
        return {
            'name': 'anthropic',
            'url': ANTHROPIC_API_URL,
            'headers': {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
            },
            'model': model,
            'delay': 0,
            'api_key': api_key,
        }

    # Default: github
    token = _resolve_token()
    model = os.environ.get('LLM_MODEL', 'gpt-4o-mini')
    return {
        'name': 'github',
        'url': GITHUB_API_URL,
        'headers': {
            'Authorization': f'Bearer {token}' if token else '',
            'Content-Type': 'application/json',
        },
        'model': model,
        'delay': 0.5,
        'token': token,
    }


def _resolve_token():
    """Resolve GitHub token: env var → gh CLI → None."""
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token

    try:
        result = subprocess.run(
            ['gh', 'auth', 'token'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def _check_ollama():
    """Check if Ollama is reachable. Returns True if available."""
    try:
        req = urllib.request.Request('http://localhost:11434/v1/models')
        urllib.request.urlopen(req, timeout=5)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return False


def _check_backend(backend):
    """Check if the LLM backend is available. Returns True if usable."""
    if backend['name'] == 'ollama':
        if not _check_ollama():
            print('\nLLM: Ollama not reachable at localhost:11434')
            print('  Start Ollama: ollama serve')
            return False
        print(f'\nUsing Ollama backend (model: {backend["model"]})')
        return True
    elif backend['name'] == 'anthropic':
        if not backend.get('api_key'):
            print('\nLLM: no Anthropic API key available')
            print('  Set ANTHROPIC_API_KEY environment variable')
            return False
        print(f'\nUsing Anthropic backend (model: {backend["model"]})')
        return True
    else:
        if not backend.get('token'):
            print('\nLLM: no GitHub token available')
            print('  Set GITHUB_TOKEN or install gh CLI')
            return False
        print(f'\nUsing GitHub Models backend (model: {backend["model"]})')
        return True


def _call_llm(backend, system_prompt, prompt, max_retries=5):
    """Call LLM API with exponential backoff. Returns parsed JSON dict or None."""
    if backend['name'] == 'anthropic':
        body_dict = {
            'model': backend['model'],
            'max_tokens': 1024,
            'system': system_prompt,
            'messages': [
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.1,
        }
    else:
        body_dict = {
            'model': backend['model'],
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.1,
        }
        # JSON mode: different param for Ollama vs OpenAI
        if backend['name'] == 'ollama':
            body_dict['format'] = 'json'
        else:
            body_dict['response_format'] = {'type': 'json_object'}

    body = json.dumps(body_dict).encode()

    for attempt in range(max_retries):
        req = urllib.request.Request(
            backend['url'],
            data=body,
            headers=backend['headers'],
        )

        try:
            resp = urllib.request.urlopen(req, timeout=120)
            data = json.loads(resp.read())
            # Anthropic: content[0].text; OpenAI-compatible: choices[0].message.content
            if backend['name'] == 'anthropic':
                content = data['content'][0]['text']
            else:
                content = data['choices'][0]['message']['content']
            return json.loads(content)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                delay = 10 * (2 ** attempt)
                print(f'    Rate limited (429), waiting {delay}s (attempt {attempt+1}/{max_retries})...')
                time.sleep(delay)
                continue
            print(f'    API error: {e}')
            return None
        except urllib.error.URLError as e:
            print(f'    API error: {e}')
            return None
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f'    Parse error: {e}')
            return None


def _map_relevance(llm_result):
    """Map LLM result to relevance 0-3 using category if available."""
    category = llm_result.get('category')
    confidence = llm_result.get('confidence', 0.0)

    if category:
        if category == 'layoff' and confidence >= 0.7:
            return 3
        if category == 'layoff':
            return 2
        if category == 'freeze':
            return 2
        if category == 'anxiety':
            return 1
        return 0

    # Fallback for old data without category
    is_layoff = llm_result.get('is_actual_layoff', False)
    if is_layoff and confidence >= 0.8:
        return 3
    if is_layoff and confidence >= 0.5:
        return 2
    if not is_layoff and confidence < 0.7:
        return 1
    return 0


def _build_prompt(post):
    """Build user prompt from post data."""
    parts = [
        f'Forrás: {post.get("source", "reddit")} / {post["subreddit"]}',
        f'Dátum: {post["date"]}',
        f'Cím: {post["title"]}',
    ]
    if post.get('selftext'):
        text = post['selftext'][:1500]  # limit to save tokens
        parts.append(f'Szöveg: {text}')

    comments = post.get('top_comments', [])
    if comments:
        top = comments[:5]  # top 5 comments
        comment_text = '\n'.join(
            f'- {c.get("body", "")[:200]}' for c in top
        )
        parts.append(f'Top kommentek:\n{comment_text}')

    return '\n'.join(parts)


def _estimate_manual_minutes(post):
    """Estimate how many minutes a human would need to review this post."""
    text_len = len(post.get('title', '')) + len(post.get('selftext', ''))
    comment_count = len(post.get('top_comments', []))

    if text_len < 200:
        minutes = 2
    elif text_len < 1000:
        minutes = 5
    else:
        minutes = 8

    if comment_count > 10:
        minutes += 3
    elif comment_count > 5:
        minutes += 1.5

    return minutes


def batch_triage(posts, backend=None, batch_size=50):
    """Batch triage: LLM calls to filter relevant posts by title.

    Splits posts into batches (default 50) to stay within LLM context limits.
    Returns dict {post_id: True/False} or None if all LLM calls fail.
    """
    if backend is None:
        backend = _resolve_backend()

    if not _check_backend(backend):
        print('  Batch triage SKIPPED — no LLM available')
        return None

    print(f'\nBatch triage: {len(posts)} poszt címének szűrése ({batch_size}-es batch-ekben)...')

    all_relevant_global_indices = set()
    total_batches = (len(posts) + batch_size - 1) // batch_size
    errors = 0

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(posts))
        batch = posts[start:end]

        # Build numbered title list (1-based within batch)
        numbered_titles = []
        for i, post in enumerate(batch):
            title = post.get('title', '').strip()
            subreddit = post.get('subreddit', '')
            numbered_titles.append(f'{i+1}. [r/{subreddit}] {title}')

        prompt = '\n'.join(numbered_titles)
        print(f'  Batch {batch_idx+1}/{total_batches} ({len(batch)} poszt)...', end=' ')

        if backend['delay'] > 0:
            time.sleep(backend['delay'])

        result = _call_llm(backend, TRIAGE_SYSTEM_PROMPT, prompt)

        if result is None:
            print('FAILED')
            errors += 1
            continue

        relevant_indices = result.get('relevant', [])

        # Map batch-local indices back to global indices
        for idx in relevant_indices:
            if isinstance(idx, int) and 1 <= idx <= len(batch):
                all_relevant_global_indices.add(start + idx)  # 1-based to global 1-based

        relevant_in_batch = len([i for i in relevant_indices if isinstance(i, int) and 1 <= i <= len(batch)])
        print(f'{relevant_in_batch}/{len(batch)} releváns')

    if errors == total_batches:
        print('  Összes batch FAILED — falling back to keyword filter')
        return None

    # Build result dict
    triage_results = {}
    for i, post in enumerate(posts):
        post_id = post.get('id', str(i))
        triage_results[post_id] = (i + 1) in all_relevant_global_indices

    relevant_count = sum(1 for v in triage_results.values() if v)
    print(f'  Batch triage összesítés: {relevant_count}/{len(posts)} releváns ({relevant_count*100//len(posts)}%)')

    return triage_results


def validate_posts(posts, triage_results=None):
    """Validate analyzed posts with LLM. Returns enriched post list + stats dict.

    Args:
        posts: List of analyzed post dicts.
        triage_results: Optional dict {post_id: bool} from batch_triage().
                       If provided, only posts with True are validated.
                       If None, falls back to keyword-based relevance >= 1 filter.
    """
    stats = {
        'validated': 0,
        'errors': 0,
        'skipped': 0,
        'triage_used': triage_results is not None,
        'est_input_tokens': 0,
        'est_output_tokens': 0,
        'est_manual_hours': 0.0,
        'elapsed_seconds': 0.0,
    }

    backend = _resolve_backend()

    # Check backend availability
    if not _check_backend(backend):
        print('LLM validation: SKIPPED')
        for post in posts:
            post['llm_validated'] = False
        stats['skipped'] = len(posts)
        stats['est_manual_hours'] = sum(_estimate_manual_minutes(p) for p in posts) / 60
        return posts, stats

    # Filter posts to validate: union of triage + keyword
    if triage_results is not None:
        # Union: relevant if triage says yes OR keyword relevance >= 1
        def _is_relevant(p):
            triage_yes = triage_results.get(p.get('id', ''), False)
            keyword_yes = p.get('relevance', 0) >= 1
            return triage_yes or keyword_yes
        to_validate = [p for p in posts if _is_relevant(p)]
        skip = [p for p in posts if not _is_relevant(p)]
        filter_label = 'triage + keyword union'
    else:
        # Fallback: keyword-based relevance >= 1
        to_validate = [p for p in posts if p.get('relevance', 0) >= 1]
        skip = [p for p in posts if p.get('relevance', 0) < 1]
        filter_label = 'keyword relevance >= 1'

    # Mark triage_relevant on all posts
    validate_ids = set(p.get('id', '') for p in to_validate)
    for p in posts:
        p['triage_relevant'] = p.get('id', '') in validate_ids

    for p in skip:
        p['llm_validated'] = False
    stats['skipped'] = len(skip)

    print(f'LLM validation: {len(to_validate)} posts to validate via {filter_label} (skipping {len(skip)})')

    start_time = time.time()

    for i, post in enumerate(to_validate):
        if post.get('llm_validated'):
            stats['validated'] += 1
            continue

        print(f'  [{i+1}/{len(to_validate)}] {post["title"][:50]}...')

        prompt = _build_prompt(post)

        # Estimate tokens (Hungarian text ≈ 1 token per 3 chars)
        est_input = (len(SYSTEM_PROMPT) + len(prompt)) / 3
        stats['est_input_tokens'] += int(est_input)

        if backend['delay'] > 0:
            time.sleep(backend['delay'])

        result = _call_llm(backend, SYSTEM_PROMPT, prompt)

        if result is None:
            print(f'    FAILED — keeping keyword scoring')
            post['llm_validated'] = False
            stats['errors'] += 1
            continue

        # Estimate output tokens
        result_str = json.dumps(result, ensure_ascii=False)
        stats['est_output_tokens'] += int(len(result_str) / 4)

        post['llm_validated'] = True
        post['llm_relevance'] = _map_relevance(result)
        post['llm_category'] = result.get('category', 'other')
        post['llm_company'] = result.get('company')
        post['llm_headcount'] = result.get('headcount')
        post['llm_confidence'] = result.get('confidence', 0.0)
        post['llm_summary'] = result.get('summary', '')
        post['llm_technologies'] = result.get('technologies', [])
        post['llm_roles'] = result.get('roles', [])
        post['llm_ai_role'] = result.get('ai_role', 'none')
        post['llm_ai_context'] = result.get('ai_context')
        stats['validated'] += 1

    stats['elapsed_seconds'] = time.time() - start_time
    stats['est_manual_hours'] = sum(_estimate_manual_minutes(p) for p in posts) / 60

    # Cost estimation (per-million-token rates)
    if backend['name'] == 'anthropic':
        input_rate = 0.80   # Haiku 4.5
        output_rate = 4.00
    else:
        input_rate = 0.15   # gpt-4o-mini
        output_rate = 0.60
    est_input_cost = stats['est_input_tokens'] / 1_000_000 * input_rate
    est_output_cost = stats['est_output_tokens'] / 1_000_000 * output_rate
    est_total_cost = est_input_cost + est_output_cost

    print(f'\nLLM validation complete:')
    print(f'  Backend: {backend["name"]} ({backend["model"]})')
    print(f'  Filter: {filter_label}')
    print(f'  Validated: {stats["validated"]}')
    print(f'  Errors: {stats["errors"]}')
    print(f'  Skipped: {stats["skipped"]}')
    print(f'  Time: {stats["elapsed_seconds"]:.0f}s')
    print(f'  Est. tokens: ~{stats["est_input_tokens"]:,} input + ~{stats["est_output_tokens"]:,} output')
    if backend['name'] == 'ollama':
        print(f'  Cost: $0.00 (local)')
    elif backend['name'] == 'anthropic':
        print(f'  Est. cost (Haiku rates): ${est_total_cost:.3f}')
    else:
        print(f'  Est. cost (gpt-4o-mini rates): ${est_total_cost:.3f}')
        print(f'  Actual cost (GitHub Models): $0.00')
    print(f'  Manual equivalent: ~{stats["est_manual_hours"]:.0f} hours')

    return posts, stats


def save_validated_posts(posts, output_path='data/validated_posts.json'):
    """Save validated posts to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f'Saved {len(posts)} validated posts to {output_path}')


if __name__ == '__main__':
    with open('data/analyzed_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    validated = validate_posts(posts)
    save_validated_posts(validated)
