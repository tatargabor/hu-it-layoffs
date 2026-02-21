## MODIFIED Requirements

### Requirement: LLM válasz-séma tartalmaz category mezőt

A `SYSTEM_PROMPT` JSON válasz-sémája SHALL tartalmazza a `category` mezőt a következő értékekkel: `layoff`, `freeze`, `anxiety`, `other`. A prompt SHALL definiálja mindegyik kategória jelentését és SHALL tartalmazzon példát minden kategóriára.

A `freeze` kategória SHALL kizárólag tényleges munkaerőpiaci jelzésekre vonatkozzon:
- Nehéz elhelyezkedés, felvételi stop, álláspiac-romlás konkrét tapasztalata
- Egyéni elbocsátás utáni álláskeresés

A `freeze` kategória SHALL NEM vonatkozzon:
- Home office / remote munka viták (nem munkaerőpiaci esemény)
- Karriertanács, "merre menjek" típusú kérdések
- Munka-magánélet egyensúly, kiégés, karrierszünet
- Álláskereső portál ajánlás, bérkérdés
- Általános remote munka jövője kérdés

#### Scenario: LLM layoff kategóriát ad közvetlen leépítés posztra
- **WHEN** a poszt konkrét IT leépítésről szól (pl. "Ericsson 200 embert bocsát el")
- **THEN** az LLM válasz `category` mezője `layoff` értéket tartalmaz

#### Scenario: LLM freeze kategóriát ad álláspiac-romlás posztra
- **WHEN** a poszt hiring freeze-ről, nehéz elhelyezkedésről szól (pl. "Lassan egy éve nem találok munkát")
- **THEN** az LLM válasz `category` mezője `freeze` értéket tartalmaz

#### Scenario: LLM other kategóriát ad home office vita posztra
- **WHEN** a poszt home office / remote munka vitáról szól (pl. "Home office hátrafelé sült el")
- **THEN** az LLM válasz `category` mezője `other` értéket tartalmaz

#### Scenario: LLM other kategóriát ad karriertanács posztra
- **WHEN** a poszt karriertanácsot kér (pl. "Megéri váltani több pénzért?", "Ki mire váltana IT-ról?")
- **THEN** az LLM válasz `category` mezője `other` értéket tartalmaz

#### Scenario: LLM other kategóriát ad remote munka kérdésre
- **WHEN** a poszt remote munka jövőjéről kérdez (pl. "Mennyire lesz nehéz full-remote munkát találni?")
- **THEN** az LLM válasz `category` mezője `other` értéket tartalmaz

### Requirement: SYSTEM_PROMPT szektor definíciók szigorítása

A `SYSTEM_PROMPT` sector mező leírása SHALL explicit negatív példákat tartalmazzon:
- `retail tech`: "CSAK e-commerce platform, online kereskedelem, webshop, szállásfoglaló/utazási TECH cég (Szállás Group, hasznaltauto.hu). NEM: fizikai bolt, áruház, barkácsáruház leépítés (OBI, BestByte, Tesco, Aldi = sector: 'other')"
- `automotive`: prompt SHALL jelezze hogy "Audi/Suzuki/Mercedes GYÁRI MUNKÁS/targoncás/termelési dolgozó leépítés = category: 'other'. CSAK fejlesztőközpont/szoftvermérnök/IT pozíciók = category: 'layoff'"
- `entertainment`: prompt SHALL jelezze hogy "Operaház, TV csatorna, mozi = sector: 'other', KIVÉVE ha IT pozíciókat érint"

#### Scenario: OBI barkácsáruház sector other
- **WHEN** az LLM egy OBI leépítés posztot validál
- **THEN** az LLM válasz `sector` mezője `other` és `category` mezője `other`

#### Scenario: BestByte elektronikai bolt sector other
- **WHEN** az LLM egy BestByte boltzárás/leépítés posztot validál
- **THEN** az LLM válasz `sector` mezője `other` és `category` mezője `other`

#### Scenario: Szállás Group megmarad retail tech
- **WHEN** az LLM egy Szállás Group leépítés posztot validál (IT fejlesztők érintettek)
- **THEN** az LLM válasz `sector` mezője `retail tech` és `category` mezője `layoff`

#### Scenario: Audi gyári munkás sector automotive category other
- **WHEN** az LLM egy Audi győri gyári munkás leépítés posztot validál
- **THEN** az LLM válasz `sector` mezője `automotive` és `category` mezője `other`

#### Scenario: Audi fejlesztőközpont sector automotive category layoff
- **WHEN** az LLM egy Audi fejlesztőközpont szoftvermérnök leépítés posztot validál
- **THEN** az LLM válasz `sector` mezője `automotive` és `category` mezője `layoff`

### Requirement: Event label konzisztencia utasítás

A `SYSTEM_PROMPT` event_label leírása SHALL tartalmazzon konzisztencia utasítást: "Ugyanarról a cégről/cégcsoportról szóló posztok UGYANAZT az event_label-t kapják. Ha a cég több néven ismert (pl. Docler/Byborg/Gattyán), használd a legismertebb nevet. NE hozz létre külön labelt aliasoknak."

#### Scenario: Docler és Byborg posztok egységes label
- **WHEN** az LLM validál egy "Docler Holding leépítés" és egy "Byborg home office eltörlés" posztot
- **THEN** mindkét poszt event_label-je ugyanazt a cégcsoport nevet használja (pl. "Docler Holding 2025 Q4 leépítés")

#### Scenario: Ugyanaz a cég különböző hírcikkekből
- **WHEN** több hírcikk ugyanarról az OTP leépítésről szól különböző forrásokból
- **THEN** mindegyik poszt event_label-je azonos (pl. "OTP Bank 2025 Q1 leépítés")

### Requirement: Footer és branding eltávolítása

A `generate_html()` által generált HTML SHALL NEM tartalmazzon "powered by Claude Code · OpenSpec" vagy "Specifikálva OpenSpec-kel, generálva Claude Code-dal" szöveget.

#### Scenario: Footer nem tartalmaz Claude Code hivatkozást
- **WHEN** a dashboard HTML-t generáljuk
- **THEN** a footer és header NEM tartalmaz "Claude Code" vagy "OpenSpec" szöveget
