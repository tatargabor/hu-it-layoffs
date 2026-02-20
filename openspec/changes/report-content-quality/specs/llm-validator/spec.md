## llm-validator — IT szektor fókusz és relevancia pontosítás

### Requirement: TRIAGE_SYSTEM_PROMPT IT fókusz

A triage prompt marad bőkezű (inkább false positive), de hozzáadni:
- "Leépítés, elbocsátás **az IT/tech szektorban vagy IT osztályokon**"
- NEM releváns listához: "Nem-IT szektorok leépítései (katonai, oktatási, agrár, gyártási, közlekedési) — KIVÉVE ha kifejezetten IT/tech pozíciókat érintenek"

### Requirement: SYSTEM_PROMPT kategória-definíciók szigorítása

A `category` mező definíciói jelenleg nem szűrnek szektorra. Módosítás:

**layoff** definíció (jelenlegi → új):
```
Jelenlegi: "Konkrét elbocsátás, leépítés, létszámcsökkentés"
Új:        "Konkrét IT/tech szektorban történő elbocsátás, leépítés, létszámcsökkentés.
            Ide tartozik: tech cégek, IT szolgáltatók, telco, valamint más szektorok
            IT/tech osztályai (pl. bank IT, autógyár fejlesztőközpont).
            NEM ide tartozik: katonai, oktatási, agrár, gyártási, közlekedési
            szektorok leépítései, kivéve ha kifejezetten IT pozíciókat érintenek."
```

**is_actual_layoff** definíció (jelenlegi → új):
```
Jelenlegi: "true ha a poszt konkrét IT leépítésről/elbocsátásról szól"
Új:        "true ha a poszt SZERVEZETI SZINTŰ IT/tech leépítésről szól
            (cég elbocsát N embert). False ha egyéni szintű ('kirúgtak és
            tanácsot kérek' típusú poszt) — ezek category=freeze vagy anxiety."
```

### Requirement: Személyes tanácskérés posztok helyes kategorizálása

Példák amiket a prompt-nak kezelnie kell:

| Poszt típus | Helyes category | is_actual_layoff | Helyes relevancia |
|---|---|---|---|
| "Ericsson 200 embert bocsát el" | layoff | true | 3 |
| "Kirúgtak és tanácsot kérek junior FE-ként" | freeze | false | 2 |
| "8 év alatt 3x rúgtak ki, mi legyen?" | anxiety | false | 1 |
| "Magyar Honvédség átszervezése" | other | false | 0 |
| "Corvinus nyelvtanárok leépítése" | other | false | 0 |
| "OTP IT osztályon leépítés" | layoff | true | 3 |

### Requirement: Cégszűrés a statisztikákban

A `report.py` és `visualize.py` cég-számításánál kiszűrni:
- Névtelen/általános entitásokat: ha a cégnév tartalmaz "nagyobb", "egy cég", "élelmiszerlánc" típusú általánosságot
- Megoldás: egyszerű szűrő függvény `_is_named_company(name)` mindkét fájlban

```python
_GENERIC_PATTERNS = ['nagyobb', 'kisebb', 'egy cég', 'élelmiszerlánc', 'nem nevezett']

def _is_named_company(name):
    if not name:
        return False
    lower = name.lower()
    return not any(p in lower for p in _GENERIC_PATTERNS)
```
