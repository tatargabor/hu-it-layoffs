## Context

A jelenlegi pipeline lokálisan fut (`python -m src.run`). Az LLM validáció két backend-et támogat:
- **GitHub Models** (`gpt-4o-mini`): ingyenes, de rate limit (429) ~44 poszt után megtöri a futtatást
- **Ollama** (`llama3.1`): megbízható, de helyi GPU/gép kell

CI automatizáláshoz egy megbízható, fizetős API backend kell. Az Anthropic API (Haiku 4.5) erre ideális.

Jelenlegi LLM architektúra (`llm_validator.py`):
- `_resolve_backend()` → config dict (url, headers, model, delay)
- `_call_llm(backend, system_prompt, prompt)` → OpenAI-kompatibilis `/chat/completions` endpoint
- Mindkét backend (github, ollama) ugyanazt az OpenAI formátumot használja

Az Anthropic API **más formátumú**: `/v1/messages` endpoint, `system` paraméter a body-ban (nem messages array-ben), `content[0].text` válasz (nem `choices[0].message.content`).

## Goals / Non-Goals

**Goals:**
- Anthropic Messages API natív támogatás az `llm_validator.py`-ban
- GitHub Actions workflow ami naponta futtatja a teljes pipeline-t
- A meglévő backend-ek (github, ollama) változatlanok maradnak
- Env var alapú konfiguráció (`LLM_BACKEND=anthropic`)

**Non-Goals:**
- OpenAI-kompatibilis proxy (LiteLLM) — túl sok overhead egy ilyen kis projekthez
- Sonnet/Opus használata — Haiku 4.5 elég ehhez a feladathoz
- Reddit API auth — a `old.reddit.com` JSON API auth nélkül működik CI-ből is
- A meglévő Pages deploy workflow módosítása — az a `data/` push-ra triggerel, megmarad

## Decisions

### 1. Natív Anthropic API a `_call_llm`-ben (nem OpenAI proxy)

**Választás**: Elágazás a `_call_llm()` függvényben az Anthropic API formátumra.

**Alternatívák**:
- LiteLLM proxy: extra dependency, containerizáció, túl sok overhead
- Anthropic Python SDK: extra pip dependency — inkább `urllib` marad a meglévő mintával konzisztensen

**Indoklás**: A projekt semmilyen külső dependency-t nem használ (nincs `requests`, nincs `praw`), mindent `urllib`-bel old meg. Maradjunk ennél a mintánál. Az Anthropic API egyszerű REST, `urllib`-bel jól kezelhető.

### 2. Haiku 4.5 mindkét lépéshez (triage + validate)

**Választás**: `claude-haiku-4-5-20241022` triage-hoz és validáláshoz is.

**Alternatívák**:
- Haiku triage + Sonnet validate: ~3x drágább validate lépés, nem indokolt
- Sonnet mindkettőhöz: ~10x drágább, overkill

**Indoklás**: A feladat magyar szöveg kategorizálás strukturált JSON output-tal. Haiku 4.5 kiválóan kezeli a magyart és a few-shot JSON generálást. ~$0.04/futás vs ~$0.40/futás Sonnet-tel.

### 3. Pipeline workflow: run → commit → push (Pages triggert a meglévő workflow kezeli)

**Választás**: Új `pipeline.yml` ami futtatja a pipeline-t, commitol és push-ol. A meglévő `report.yml` (Pages deploy) a `data/` push-ra triggerel, nem kell hozzányúlni.

**Alternatívák**:
- Egyetlen összeolvasztott workflow: bonyolultabb, nehezebb karbantartani
- Külön deploy step a pipeline-ban: duplikáció a meglévő workflow-val

**Indoklás**: Szeparált felelősségek — a pipeline workflow adatot generál, a Pages workflow deploy-ol. Ha bármelyik változik, a másik nem érintett.

### 4. Token: `ANTHROPIC_API_KEY` repo secret

**Választás**: GitHub repo secret-ként tárolt API kulcs, `${{ secrets.ANTHROPIC_API_KEY }}` env var.

**Indoklás**: Szabványos GitHub Actions minta. Lokális fejlesztéshez `ANTHROPIC_API_KEY` env var vagy `.env` fájl.

## Risks / Trade-offs

- **[Anthropic API változás]** → Az API stabil (v1), de a `urllib` wrapper nem ad SDK-szintű verziókövető védelmet. Mitigation: a válasz formátum egyszerű, könnyű javítani ha változik.
- **[Reddit rate limit CI-ből]** → Az `old.reddit.com` JSON API-t User-Agent-tel hívjuk, ez CI IP-ről is működik, de Reddit blokkolhatja. Mitigation: ha scrape fail-el, a pipeline 0-val lép ki (nincs adat változás, nincs commit).
- **[Költség kontroll]** → Haiku ~$0.04/futás, napi 1x = ~$1.2/hó. Mitigation: cron napi 1x (nem 2x mint a korábbi v2-ci spec-ben), és `workflow_dispatch` kézi futtatáshoz.
- **[Git push conflict]** → Ha párhuzamosan fut két pipeline (cron + manual), a push ütközhet. Mitigation: concurrency group cancel-in-progress-szel.
