"""LLM validator — validates analyzed posts using GitHub Models API (gpt-4o-mini)."""

import json
import os
import subprocess
import time
import urllib.request
import urllib.error


API_URL = 'https://models.inference.ai.azure.com/chat/completions'
MODEL = 'gpt-4o-mini'
REQUEST_DELAY = 0.5

SYSTEM_PROMPT = """Te egy magyar IT szektorral foglalkozó elemző vagy. A feladatod Reddit posztok validálása: eldönteni hogy egy poszt ténylegesen IT leépítésről/elbocsátásról szól-e, vagy sem.

Válaszolj JSON formátumban az alábbi sémával:
{
  "is_actual_layoff": true/false,
  "confidence": 0.0-1.0,
  "company": "cégnév vagy null",
  "headcount": szám vagy null,
  "summary": "1 mondatos magyar összefoglaló",
  "technologies": ["technológia1", "technológia2"],
  "roles": ["munkakör1", "munkakör2"]
}

Mezők:
- is_actual_layoff: true ha a poszt konkrét IT leépítésről/elbocsátásról szól (nem csak kérdez róla, nem csak általánosságban beszél)
- confidence: mennyire vagy biztos (0.0 = teljesen bizonytalan, 1.0 = teljesen biztos)
- company: az érintett cég neve ha azonosítható, egyébként null
- headcount: becsült érintett létszám ha kiderül a posztból, egyébként null
- summary: 1 mondatos magyar összefoglaló a poszt lényegéről
- technologies: programozási nyelvek, keretrendszerek, eszközök amik a posztban szerepelnek (pl. "Java", "React", "SAP", "Kubernetes"). Üres lista ha nincs ilyen.
- roles: munkakörök, pozíciók amik a posztban szerepelnek (pl. "backend fejlesztő", "DevOps", "QA", "project manager"). Üres lista ha nincs ilyen.

Példák:

Poszt: "Ericsson 200 embert bocsát el Budapesten, főleg firmware és embedded fejlesztők érintettek"
Válasz: {"is_actual_layoff": true, "confidence": 0.95, "company": "Ericsson", "headcount": 200, "summary": "Az Ericsson 200 firmware és embedded fejlesztőt bocsát el budapesti irodájából.", "technologies": ["firmware", "embedded"], "roles": ["firmware fejlesztő", "embedded fejlesztő"]}

Poszt: "Megéri programozónak tanulni 2025-ben? Merre menjek?"
Válasz: {"is_actual_layoff": false, "confidence": 0.9, "company": null, "headcount": null, "summary": "Karriertanács kérés, nem leépítésről szól.", "technologies": [], "roles": ["programozó"]}

FONTOS: Csak JSON-t válaszolj, semmi mást!"""


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


def _call_llm(token, prompt, max_retries=5):
    """Call GitHub Models API with exponential backoff. Returns parsed JSON dict or None."""
    body = json.dumps({
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt},
        ],
        'response_format': {'type': 'json_object'},
        'temperature': 0.1,
    }).encode()

    for attempt in range(max_retries):
        req = urllib.request.Request(
            API_URL,
            data=body,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
        )

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            content = data['choices'][0]['message']['content']
            return json.loads(content)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                delay = 10 * (2 ** attempt)  # 10s, 20s, 40s, 80s, 160s
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
    """Map LLM result to relevance 0-3."""
    is_layoff = llm_result.get('is_actual_layoff', False)
    confidence = llm_result.get('confidence', 0.0)

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


def validate_posts(posts):
    """Validate analyzed posts with LLM. Returns enriched post list + stats dict."""
    stats = {
        'validated': 0,
        'errors': 0,
        'skipped': 0,
        'est_input_tokens': 0,
        'est_output_tokens': 0,
        'est_manual_hours': 0.0,
        'elapsed_seconds': 0.0,
    }

    token = _resolve_token()

    if not token:
        print('\nLLM validation: SKIPPED (no GitHub token available)')
        print('  Set GITHUB_TOKEN or install gh CLI for LLM validation')
        for post in posts:
            post['llm_validated'] = False
        stats['skipped'] = len(posts)
        # Still estimate manual time
        stats['est_manual_hours'] = sum(_estimate_manual_minutes(p) for p in posts) / 60
        return posts, stats

    # Filter to relevant posts only
    to_validate = [p for p in posts if p.get('relevance', 0) >= 1]
    skip = [p for p in posts if p.get('relevance', 0) < 1]

    for p in skip:
        p['llm_validated'] = False
    stats['skipped'] = len(skip)

    print(f'\nLLM validation: {len(to_validate)} posts to validate (skipping {len(skip)} irrelevant)')

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

        time.sleep(REQUEST_DELAY)

        result = _call_llm(token, prompt)

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
        post['llm_company'] = result.get('company')
        post['llm_headcount'] = result.get('headcount')
        post['llm_confidence'] = result.get('confidence', 0.0)
        post['llm_summary'] = result.get('summary', '')
        post['llm_technologies'] = result.get('technologies', [])
        post['llm_roles'] = result.get('roles', [])
        stats['validated'] += 1

    stats['elapsed_seconds'] = time.time() - start_time
    stats['est_manual_hours'] = sum(_estimate_manual_minutes(p) for p in posts) / 60

    # Cost estimation (gpt-4o-mini pricing, even though GitHub Models is free)
    est_input_cost = stats['est_input_tokens'] / 1_000_000 * 0.15
    est_output_cost = stats['est_output_tokens'] / 1_000_000 * 0.60
    est_total_cost = est_input_cost + est_output_cost

    print(f'\nLLM validation complete:')
    print(f'  Validated: {stats["validated"]}')
    print(f'  Errors: {stats["errors"]}')
    print(f'  Skipped: {stats["skipped"]}')
    print(f'  Time: {stats["elapsed_seconds"]:.0f}s')
    print(f'  Est. tokens: ~{stats["est_input_tokens"]:,} input + ~{stats["est_output_tokens"]:,} output')
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
