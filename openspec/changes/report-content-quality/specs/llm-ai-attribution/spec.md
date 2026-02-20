## llm-ai-attribution — Dashboard AI count szinkronizálás

### Requirement: Egységes `_is_ai_attributed()` logika

A `visualize.py` jelenleg csak `p.get('ai_attributed')` (keyword-alapú) mezőt nézi az AI statisztikákhoz. A `report.py` viszont `_is_ai_attributed()` helper-t használ ami az LLM `ai_role` mezőt is figyelembe veszi.

Eredmény: a Szállás Group poszt (llm_ai_role="factor") megjelenik a markdown riportban mint AI-érintett, de a HTML dashboardon nem.

### Requirement: `visualize.py` AI count fix

3 helyen kell módosítani a `visualize.py`-ban:

1. **Stat card** (sor ~137): `ai_count = sum(1 for p in relevant if p.get('ai_attributed'))` → `_is_ai_attributed(p)`
2. **AI trend chart** (sor ~86): `if p.get('ai_attributed')` → `if _is_ai_attributed(p)`
3. **Detailed table** (sor ~169): `'igen' if p.get('ai_attributed')` → `'igen' if _is_ai_attributed(p)`

### Requirement: `_is_ai_attributed()` definíció

```python
def _is_ai_attributed(post):
    """Check if post is AI-attributed. Uses LLM ai_role if available, else keyword."""
    if post.get('llm_validated') and 'llm_ai_role' in post:
        return post['llm_ai_role'] in ('direct', 'factor', 'concern')
    return post.get('ai_attributed', False)
```

Ez a `report.py`-ban már létezik (sor 39-43). Azonos implementáció kell a `visualize.py`-ba.
