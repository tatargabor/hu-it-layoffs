## MODIFIED Requirements

### Requirement: Módszertan szekció a riportban

A `report.py` módszertan szekciója SHALL a tényleges pipeline-t tükrözze:

1. **Adatgyűjtés** — Reddit scraping (meglévő szöveg OK)
2. **Kulcsszó-alapú elemzés** — relevancia pontozás, cégfelismerés, AI-attribúció (meglévő szöveg OK)
3. **LLM batch triage** — posztcímek szűrése batch-ekben, releváns posztok kiválasztása
4. **LLM full validáció** — részletes elemzés: kategória, cég, szektor, AI-szerep, technológiák, munkakörök
5. **Report generálás** — Markdown + interaktív HTML dashboard

A módszertan SHALL megemlítse:
- A batch triage lépést és hogy ez szűri a validálandó posztokat
- A szektor klasszifikációt (zárt kategórialista, kontextus-alapú)
- Hogy több LLM backend támogatott (konfigurálható)

#### Scenario: Módszertan tartalmazza a batch triage lépést
- **WHEN** a report generálódik
- **THEN** a módszertan szekció tartalmazza a batch triage leírását

#### Scenario: Módszertan tartalmazza a szektor klasszifikációt
- **WHEN** a report generálódik
- **THEN** a módszertan szekció tartalmazza hogy az LLM zárt kategórialistából választ szektort

### Requirement: Költségbecslés dinamikus az llm_stats-ból

A report költségbecslés szekciója SHALL az `llm_stats` dict-ből vegye az árakat és backend nevet, ne hardcoded gpt-4o-mini árakból. Ha az llm_stats tartalmaz backend info-t, azt használja a megjelenítésben.

#### Scenario: Anthropic backend költség
- **WHEN** `llm_stats` tartalmazza `backend_name="anthropic"` infót
- **THEN** a report "Becsült költség (Anthropic Haiku áron)" feliratot használ

#### Scenario: Lokális backend költség
- **WHEN** `llm_stats` tartalmazza `backend_name="ollama"` infót
- **THEN** a report "$0.00 (lokális)" költséget jelenít meg
