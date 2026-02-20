## Why

A riport "IT Leépítés Radar" címmel fut, de a 27 "közvetlen leépítésből" 7 nem IT-s (Honvédség, Corvinus nyelvtanárok, MATE agrár, akkugyárak, Rail Cargo), ~5 további pedig személyes tanácskérés (nem szervezeti leépítési riport). Az AI-statisztika inkonzisztens: a markdown report 19 AI-posztot mutat (LLM-alapú), a HTML dashboard csak 10-et (keyword-alapú). Az "érintett cégek" között névtelen entitások szerepelnek ("nagyobb német cég", "magyar élelmiszerlánc"). Ezek együtt aláássák a riport hitelességét.

## What Changes

- **LLM prompt IT-szektorra szűkítése**: A triage és validation SYSTEM_PROMPT-ok explicit IT/tech fókuszt kapnak — nem-IT szektorbeli leépítések `other` kategóriába kerülnek
- **Relevancia-szintek pontosítása**: `is_actual_layoff` = true csak szervezeti szintű leépítésnél, egyéni "kirúgtak és tanácsot kérek" posztok max relevancia 2
- **AI count konzisztencia**: `visualize.py` ugyanazt a `_is_ai_attributed()` logikát használja mint `report.py` (LLM ai_role + keyword fallback)
- **Cégszűrés**: Névtelen/általános entitások ("nagyobb német cég") nem számítanak érintett cégnek a statisztikákban

## Capabilities

### New Capabilities
- (nincs)

### Modified Capabilities
- `llm-validator`: Triage és validation prompt IT-szektorra fókuszálása, relevancia-szint definíciók pontosítása
- `llm-ai-attribution`: Dashboard (visualize.py) AI count szinkronizálása a report.py logikájával

## Impact

- **src/llm_validator.py**: TRIAGE_SYSTEM_PROMPT és SYSTEM_PROMPT módosítás (IT fókusz, relevancia pontosítás)
- **src/visualize.py**: `ai_count` számítás átírása `_is_ai_attributed()` logikára, cég-szűrés
- **src/report.py**: Cég-szűrés (névtelen entitások kiszűrése a statisztikákból)
- Újrafuttatás szükséges a pipeline-on az új prompt-okkal
