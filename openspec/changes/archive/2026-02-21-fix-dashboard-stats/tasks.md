## 1. visualize.py stat kártyák

- [x] 1.1 `direct` lista: add `_is_it_relevant()` filter (line 167)
- [x] 1.2 "Releváns poszt" kártya → "Erős jelzés" label + pool váltás `len(relevant)` → `len(strong)` (line 535)
- [x] 1.3 `companies` set: pool váltás `relevant` → `strong` (line 263)
- [x] 1.4 `freeze_count`: `hiring_freeze_signal` → `_eff_category(p) == 'freeze'` (line 265)

## 2. visualize.py chartok

- [x] 2.1 Category chart: `p.get('category', 'other')` → `_eff_category(p)`, kizár `'other'` (line 204-206)
- [x] 2.2 Company chart: `_is_named_company()` filter a company_counts loop-ban (line 196-199)
- [x] 2.3 Engagement tábla: nyers `category` → `_eff_category()`, `'other'` sor kizárás (line 271-276, 580)
- [x] 2.4 Hiring freeze timeline chart: `hiring_freeze_signal` → `_eff_category(p) == 'freeze'` (line 225-231)

## 3. report.py szinkron

- [x] 3.1 `direct` lista: verify `_is_it_relevant()` — already present
- [x] 3.2 `companies` set: pool váltás `relevant` → `strong` (line 208)
- [x] 3.3 `freeze_count`: `hiring_freeze_signal` → `_eff_category(p) == 'freeze'` (line 214)
- [x] 3.4 `by_cat`: nyers `category` → `_eff_category()`, kizár `'other'` (line 293-308)

## 4. Verify

- [x] 4.1 Regeneráld lokálisan: `python3 -c` script a generate_html + generate_report hívással
- [x] 4.2 Stat számok: Strong=180, Direct=79, Companies=38, Freeze=72, AI=80, Categories: layoff=108/freeze=72/anxiety=44
