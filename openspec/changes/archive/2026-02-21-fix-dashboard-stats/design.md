## Context

A dashboard stat kártyák és chartok a `generate_html()` és `generate_report()` függvényekben generálódnak. Az `improve-relevance-filtering` change bevezette a `_eff_category()`, `_is_it_relevant()`, `_is_hungarian_relevant()` helpereket és az `_IT_SECTORS` whitelistet, de ezek nem lettek konzisztensen alkalmazva minden stat/chart számításra.

## Goals / Non-Goals

**Goals:**
- Minden stat kártya és chart konzisztensen használja az IT-szűrőket és LLM-alapú kategóriákat
- A "Releváns poszt" kártya cseréje "Erős jelzés"-re (informatívabb)
- Hiring freeze az LLM kategóriából számoljon

**Non-Goals:**
- Új chartok vagy stat kártyák hozzáadása
- LLM prompt módosítás
- Pipeline futtatás — csak a riport generálás változik

## Decisions

### 1. Pool konzisztencia

Három pool van: `relevant` (rel>=1), `strong` (rel>=2, IT, hungarian, not other), `direct` (rel>=3).

| Stat/Chart | Jelenlegi pool | Új pool |
|------------|---------------|---------|
| "Közvetlen leépítés" kártya | `direct` (nincs IT filter) | `direct` + `_is_it_relevant()` |
| "Releváns poszt" kártya | `relevant` | → "Erős jelzés" kártya, `strong` pool |
| "Érintett cég" kártya | `relevant` | `strong` |
| Company chart | `strong` (OK, de None leak) | `strong` + `_is_named_company()` |
| Category chart | `relevant`, nyers `category` | `relevant`, `_eff_category()`, no `'other'` |
| Engagement tábla | `relevant`, nyers `category` | `relevant`, `_eff_category()`, no `'other'` |
| Hiring freeze kártya | `hiring_freeze_signal` keyword | `_eff_category(p) == 'freeze'` |

### 2. report.py szinkron

A `generate_report()` markdown ugyanezeket a javításokat kapja: `by_cat` → `_eff_category()`, `freeze_count` → category-based, `direct` → IT filter, `companies` → `strong` pool.
