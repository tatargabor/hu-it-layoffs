## Why

A dashboard stat kártyák és chartok inkonzisztensek: a "Közvetlen leépítés" nem szűr IT szektorra, az "Érintett cég" a `relevant` (leggyengébb) poolból számol, a category chart `'other'`-t is mutat és a nyers `category` mezőt használja az LLM `_eff_category()` helyett, a company chart generikus neveket is tartalmaz, a hiring freeze a régi keyword-alapú mezőt használja az LLM kategória helyett.

## What Changes

- **`direct` lista IT szűrő**: `_is_it_relevant()` hozzáadása a `direct` listához `visualize.py`-ban (report.py-ban már megvan)
- **"Releváns poszt" → "Erős jelzés"**: stat kártya label + pool váltás `relevant` → `strong` — az "erős jelzés" informatívabb a külső szemlélő számára
- **Érintett cég pool váltás**: `relevant` → `strong` pool a company count stat kártyához
- **Company chart szűrés**: `_is_named_company()` filter a chart adatokhoz, generikus nevek kiszűrése
- **Category chart javítás**: `_eff_category()` használata `p.get('category', 'other')` helyett, `'other'` kizárása a chartból
- **Engagement tábla**: `_eff_category()` használata konzisztensen, `'other'` sor kizárása
- **Hiring freeze**: `_eff_category(p) == 'freeze'` használata a `hiring_freeze_signal` keyword mező helyett
- **report.py szinkron**: Ugyanezek a javítások a markdown riportban is (`by_cat`, `freeze_count`, `direct`, `companies`)

## Capabilities

### New Capabilities
_(nincs)_

### Modified Capabilities
_(nincs — implementációs javítás, nem spec-szintű változás)_

## Impact

- `src/visualize.py` — stat kártyák, chart adatok, engagement tábla
- `src/report.py` — markdown stat szekció (`by_cat`, `freeze_count`, `companies`)
- Nincs LLM/scraping változás — csak `generate_html()` és `generate_report()` újrafuttatás kell
