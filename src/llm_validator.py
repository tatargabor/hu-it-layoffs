"""LLM validator — validates analyzed posts using GitHub Models API or local Ollama."""

import json
import os
import re
import subprocess
import time
import urllib.request
import urllib.error

try:
    import anthropic
except ImportError:
    anthropic = None


GITHUB_API_URL = 'https://models.inference.ai.azure.com/chat/completions'
OLLAMA_API_URL = 'http://localhost:11434/v1/chat/completions'
ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'

TRIAGE_SYSTEM_PROMPT = """Te egy magyar IT munkaerőpiaci elemző vagy. A feladatod egy poszt-lista szűrése: jelöld meg melyik posztok RELEVÁNSAK a MAGYAR IT munkaerőpiac szempontjából.

FONTOS: CSAK magyar vonatkozású ÉS IT/tech szektort érintő posztokat jelölj relevánsnak!

Releváns posztok:
- Leépítés, elbocsátás, létszámcsökkentés az IT/tech szektorban Magyarországon vagy magyar munkavállalókat érintően
- Leépítés más szektorban, DE IT/tech pozíciókat érint Magyarországon (pl. bank IT osztály, autógyár fejlesztőközpont)
- Hiring freeze, felvételi stop, álláspiac-romlás a MAGYAR IT-ben
- Nehéz elhelyezkedés, álláskeresési nehézségek a MAGYAR IT-ben
- Karrier-aggodalom, bizonytalanság, pályaváltás kérdések a MAGYAR IT szektorra vonatkozóan
- AI/automatizáció hatása a MAGYAR IT munkára
- MAGYAR IT munkaerőpiaci kérdések (fizetés, piac helyzete)
- Globális tech cég leépítése CSAK AKKOR ha kifejezetten megemlíti a magyar/budapesti hatást

NEM releváns:
- Globális tech leépítések magyar vonatkozás nélkül (Amazon USA, Ubisoft Torontó, Google globális, HP, Nestlé) — még ha magyar nyelven is írták!
- Nem-IT szektorok leépítései (bolti eladó, gyári munkás, textil, élelmiszer, katonai, oktatási, agrár, közlekedési) — KIVÉVE ha kifejezetten IT/tech pozíciókat érintenek
- Barkácsáruház (OBI), elektronikai bolt (BestByte), szupermarket (Tesco, Aldi) leépítés = NEM releváns, KIVÉVE ha kifejezetten IT pozíciókat említ
- Autógyári fizikai munkás, akkugyári dolgozó, targoncás leépítés = NEM releváns, KIVÉVE ha szoftvermérnök/fejlesztő érintett
- Kórházi, egyetemi, operaházi, TV csatornai leépítés = NEM releváns, KIVÉVE ha IT pozíciókat említ
- Külföldi leépítések magyar vonatkozás nélkül (Dél-Korea, Szlovákia, Románia — kivéve ha magyar hatást említ)
- Karriertanács, álláskereső posztok: "merre menjek?", "CV tippek", "milyen skilleket tanuljak?", "megéri váltani?" — ezek NEM munkaerőpiaci események
- Generikus AI/automatizáció cikkek konkrét cég/esemény nélkül: "300 millió munkahely szűnik meg", "AI elveszi a munkát" — ezek NEM specifikus leépítések
- Technikai kérdések, tanulási kérdések, általános politika/gazdaság
- Szórakozás, mém, offtopic

Válaszolj JSON formátumban: {"relevant": [1, 5, 12, ...]}
Ahol a számok a releváns posztok SORSZÁMAI (1-től kezdve).

FONTOS: Ha kétes a magyar vonatkozás, inkább jelöld relevánsnak. De ha egyértelműen külföldi hír magyar nyelven, NE jelöld! Csak JSON-t válaszolj!"""

SYSTEM_PROMPT = """Te egy magyar IT szektorral foglalkozó elemző vagy. A feladatod Reddit posztok kategorizálása az IT munkaerőpiac szempontjából.

Válaszolj JSON formátumban az alábbi sémával:
{
  "is_actual_layoff": true/false,
  "category": "layoff|freeze|anxiety|other",
  "confidence": 0.0-1.0,
  "company": "cégnév vagy null",
  "sector": "fintech|automotive|telecom|big tech|IT services|entertainment|energy|retail tech|startup|government|general IT|other|null",
  "headcount": szám vagy null,
  "summary": "1 mondatos magyar összefoglaló",
  "technologies": ["technológia1", "technológia2"],
  "roles": ["munkakör1", "munkakör2"],
  "ai_role": "direct|factor|concern|none",
  "ai_context": "1 mondatos magyarázat vagy null",
  "hungarian_relevance": "direct|indirect|none",
  "hungarian_context": "1 mondatos magyarázat vagy null",
  "event_label": "normalizált esemény azonosító vagy null"
}

Mezők:
- is_actual_layoff: true CSAK ha a poszt SZERVEZETI SZINTŰ leépítésről szól ÉS kifejezetten IT/tech/fejlesztő/programozó/informatikus pozíciókat érint. False ha: egyéni szintű ("kirúgtak és tanácsot kérek"), gyári/termelési/fizikai munkás leépítés, vagy nem leépítés. FONTOS: autógyári, gyártóüzemi leépítés (pl. Audi Győr gyári munkások, Suzuki termelés) NEM is_actual_layoff, KIVÉVE ha a cikk kifejezetten megemlíti, hogy IT/szoftverfejlesztő/mérnök pozíciókat érint (pl. "fejlesztőközpont bezárás", "szoftveres csapat leépítése").
- category: a poszt kategóriája az alábbiak közül:
  - "layoff": Konkrét leépítés amely IT/tech/fejlesztő/programozó/informatikus pozíciókat érint. Ide tartozik: tech cégek, IT szolgáltatók, telco, valamint más szektorok IT/tech osztályai (pl. bank IT osztály, autógyár FEJLESZTŐKÖZPONT/szoftvermérnökök). NEM ide tartozik: gyári/termelési munkás leépítés (még ha tech cégnél is!), katonai, oktatási, agrár, gyártási, közlekedési szektorok leépítései. Ha egy cikk csak annyit mond hogy "leépítés az X cégnél" és NEM említ IT/fejlesztő/programozó pozíciókat, és a cég nem IT cég → category: "other". Egyéni "kirúgtak és tanácsot kérek" típusú posztok NEM layoff — azok freeze vagy anxiety.
  - "freeze": Hiring freeze, álláspiac-romlás, nehéz elhelyezkedés, felvételi stop (pl. "egy éve nem találok munkát", "nem vesznek fel senkit"). Ide tartoznak azok a posztok is ahol valakit egyénileg elbocsátottak és tanácsot kér (nem szervezeti leépítés). FONTOS: NEM freeze a következő: home office / remote munka viták, karriertanács ("merre menjek", "megéri váltani"), munka-magánélet egyensúly, kiégés, karrierszünet, álláskereső portál ajánlás, bérkérdés, általános remote munka jövője kérdés — ezek mind 'other'!
  - "anxiety": Karrier-aggodalom, bizonytalanság, kiégés, pályaváltás kérdések az IT szektorra vonatkozóan (pl. "megéri programozónak tanulni?", "AI elveszi a munkánkat?")
  - "other": Nem kapcsolódik az IT munkaerőpiachoz — általános kérdés, hír, offtopic, VAGY nem-IT szektorban történő leépítés (katonai, oktatási, agrár, közlekedési stb.)
- confidence: mennyire vagy biztos a category besorolásban (0.0-1.0)
- company: az érintett cég neve ha azonosítható, egyébként null
- sector: az érintett iparág/szektor az alábbiak közül (a poszt kontextusából határozd meg, nem kell hozzá cégnév):
  - "fintech": bank, pénzügyi szolgáltató, fizetési rendszer IT
  - "automotive": autógyár, autóipari beszállító, járműtechnológia. FONTOS: Audi/Suzuki/Mercedes/BMW GYÁRI MUNKÁS/targoncás/termelési dolgozó/akkugyári dolgozó leépítés = category: 'other'. CSAK fejlesztőközpont/szoftvermérnök/IT pozíciók = category: 'layoff'
  - "telecom": telekommunikáció, hálózati infrastruktúra
  - "big tech": nagy nemzetközi tech cég (Microsoft, Google, Meta, stb.)
  - "IT services": IT outsourcing, tanácsadás, rendszerintegrátor
  - "entertainment": szórakoztató ipar, média, gaming tech
  - "energy": energiaszektor IT, olaj/gáz tech
  - "retail tech": CSAK e-commerce platform, online kereskedelem, webshop, szállásfoglaló/utazási TECH cég (Szállás Group, hasznaltauto.hu). NEM: fizikai bolt, áruház, barkácsáruház leépítés (OBI, BestByte, Tesco, Aldi = sector: 'other')
  - "startup": startup, kis tech cég
  - "government": állami IT, közigazgatási rendszer
  - "general IT": IT szektor, de konkrét szegmens nem azonosítható (pl. általános álláspiac, karrierkérdés)
  - "other": nem-IT szektor vagy nem besorolható
  - null: a poszt nem ad elég kontextust szektormeghatározáshoz
- headcount: becsült érintett létszám ha kiderül a posztból, egyébként null
- summary: 1 mondatos magyar összefoglaló a poszt lényegéről
- technologies: programozási nyelvek, keretrendszerek, eszközök amik a posztban szerepelnek (pl. "Java", "React", "SAP", "Kubernetes"). Üres lista ha nincs ilyen.
- roles: munkakörök, pozíciók amik a posztban szerepelnek (pl. "backend fejlesztő", "DevOps", "QA", "project manager"). Üres lista ha nincs ilyen.
- ai_role: az AI/automatizáció szerepe a posztban:
  - "direct": AI/automatizáció közvetlen oka a leépítésnek/változásnak (pl. "AI-val kiváltották a tesztelőket", "robotizáció miatt szűkítettek")
  - "factor": AI/automatizáció háttér-szerepet játszik (pl. "az AI által megoldott fejlesztések miatt kevesebb ember kell")
  - "concern": AI-val kapcsolatos szorongás, aggodalom (pl. "megéri tanulni, ha AI elveszi a munkát?", "ChatGPT kiváltja a juniorokat")
  - "none": nincs AI/automatizáció vonatkozás
- ai_context: ha ai_role nem "none", 1 mondatos magyar magyarázat az AI szerepéről. Ha ai_role "none", legyen null.
- hungarian_relevance: a poszt magyar vonatkozása:
  - "direct": Magyarországon történik, magyar céget érint, vagy magyar munkavállalók érintettek (pl. OTP, Ericsson Budapest, Szállás Group, magyar álláspiac)
  - "indirect": Globális cég leépítése ahol a cégnek ismert magyar jelenléte van, VAGY a cikk/poszt kifejezetten megemlíti a magyar hatást (pl. "Continental globális leépítés, Budapestet is érinti")
  - "none": Semmi magyar vonatkozás — külföldi cég külföldi leépítése, még ha magyar nyelven is írták (pl. "Amazon 14 ezer embert küld el az USA-ban", "Ubisoft torontói stúdió leépítés", "Dél-Korea AI munkahelyek")
- hungarian_context: ha hungarian_relevance nem "none", 1 mondatos magyarázat a magyar vonatkozásról. Ha "none", legyen null.
- event_label: normalizált esemény azonosító formátumban: "[Cég] [Helyszín opcionális] [Év QN] [típus]". Példák: "Audi Győr 2026 Q1 leépítés", "OTP Bank 2026 Q1 leépítés", "Bosch Németország 2025 Q3 leépítés". Ha a poszt nem konkrét eseményről szól (pl. általános aggodalom, álláspiac kérdés), legyen null. FONTOS: ugyanarról az eseményről szóló különböző cikkek/posztok UGYANAZT a labelt kapják! Ugyanarról a cégről/cégcsoportról szóló posztok UGYANAZT az event_label-t kapják. Ha a cég több néven ismert (pl. Docler/Byborg/Gattyán), használd a legismertebb nevet. NE hozz létre külön labelt aliasoknak.

FONTOS A MAGYAR VONATKOZÁSRÓL:
- Magyar NYELVŰ cikk NEM jelent magyar VONATKOZÁST! A Portfolio.hu, HVG, Index cikkei gyakran globális híreket tárgyalnak magyarul — ezek "none" ha nincs magyar szál.
- Globális tech cégek (Amazon, Google, Meta, Microsoft, HP, Nestlé) leépítése CSAK akkor "direct" vagy "indirect", ha kifejezetten magyar munkavállalókat vagy budapesti irodát említ.
- Reddit r/programmingHungary és r/hungary posztjai általában "direct" — a közösség magyar kontextusban beszél.

FONTOS A NEM-IT SZEKTOROKRÓL:
- Bolti eladó, áruházi dolgozó, gyári munkás, textilipari dolgozó, élelmiszeripari dolgozó leépítése = category: "other", sector: "other" — MÉG HA magyar vonatkozású is!
- Heineken, Nestlé, Dacia gyári leépítés = category: "other" (hacsak nem IT pozíciókat érint)
- Barkácsáruház, élelmiszerlánc leépítés = category: "other"
- AUTÓGYÁRI leépítés (Audi, Suzuki, Mercedes, BMW gyári munkás/termelési pozíciók) = category: "other", sector: "automotive" — KIVÉVE ha a cikk kifejezetten IT/fejlesztő/szoftver pozíciókat említ!
- CSAK akkor "layoff" ha IT/tech pozíciók érintettek (fejlesztő, programozó, informatikus, szoftvermérnök, DevOps, QA, data engineer, stb.)
- Ha a cikk csak annyit mond "leépítés a cégnél" és NEM részletezi hogy milyen pozíciók, és a cég nem IT cég → category: "other"

Példák:

Poszt: "Ericsson 200 embert bocsát el Budapesten, főleg firmware és embedded fejlesztők érintettek"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.95, "company": "Ericsson", "sector": "telecom", "headcount": 200, "summary": "Az Ericsson 200 firmware és embedded fejlesztőt bocsát el budapesti irodájából.", "technologies": ["firmware", "embedded"], "roles": ["firmware fejlesztő", "embedded fejlesztő"], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Az Ericsson budapesti irodájában történő leépítés, magyar munkavállalók érintettek."}

Poszt: "Szállás Group közel 70 fejlesztőt bocsát el, az AI által megoldott fejlesztések az indoklás"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.95, "company": "Szállás Group", "sector": "retail tech", "headcount": 70, "summary": "A Szállás Group 70 fejlesztőt bocsát el, AI-val indokolva.", "technologies": ["AI"], "roles": ["fejlesztő"], "ai_role": "factor", "ai_context": "A cég az AI-val kiváltott fejlesztésekkel indokolta a leépítést.", "hungarian_relevance": "direct", "hungarian_context": "Magyar cég (Szállás Group), magyar fejlesztők érintettek."}

Poszt: "Lassan egy éve nem találok munkát, merre tovább?"
Válasz: {"is_actual_layoff": false, "category": "freeze", "confidence": 0.85, "company": null, "sector": "general IT", "headcount": null, "summary": "A szerző egy éve nem talál IT munkát, az álláspiac beszűkült.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar IT álláspiacról szóló poszt."}

Poszt: "Megéri programozónak tanulni 2025-ben? AI elveszi a munkánkat?"
Válasz: {"is_actual_layoff": false, "category": "anxiety", "confidence": 0.9, "company": null, "sector": "general IT", "headcount": null, "summary": "Karrier-aggodalom az AI hatásáról az IT szektorra.", "technologies": ["AI"], "roles": ["programozó"], "ai_role": "concern", "ai_context": "A szerző az AI munkaerőpiaci hatása miatt aggódik.", "hungarian_relevance": "direct", "hungarian_context": "Magyar közösségben feltett kérdés a magyar IT munkaerőpiacról."}

Poszt: "Continental AI Center Budapest leépítés — a divízió áthelyezése az ok"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.9, "company": "Continental", "sector": "automotive", "headcount": null, "summary": "A Continental budapesti AI Center-ben leépítés a divízió áthelyezése miatt.", "technologies": ["AI"], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "A Continental budapesti AI Center-jében történő leépítés."}

Poszt: "Partizán interjú egy kirúgott katonával — a Magyar Honvédség átszervezése"
Válasz: {"is_actual_layoff": false, "category": "other", "confidence": 0.95, "company": "Magyar Honvédség", "sector": "other", "headcount": null, "summary": "Katonai átszervezés a Magyar Honvédségnél, nem IT szektor.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar szervezet, de nem IT szektor."}

Poszt: "Költségoptimalizálásra hivatkozva leépítik az idegennyelv-oktatást a Corvinuson"
Válasz: {"is_actual_layoff": false, "category": "other", "confidence": 0.95, "company": "Corvinus Egyetem", "sector": "other", "headcount": null, "summary": "Nyelvtanárok elbocsátása a Corvinuson, nem IT pozíciók.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar intézmény, de nem IT pozíciók."}

Poszt: "Banki IT osztályon nagy leépítés, belső fejlesztés megszűnik"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.85, "company": null, "sector": "fintech", "headcount": null, "summary": "Egy bank IT osztályán leépítés, a belső fejlesztés megszűnik.", "technologies": [], "roles": ["fejlesztő"], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar banki IT osztályon történő leépítés."}

Poszt: "Junior Frontend fejlesztőnek tanács? 2 év után leépítés volt a cégnél"
Válasz: {"is_actual_layoff": false, "category": "freeze", "confidence": 0.85, "company": null, "sector": "general IT", "headcount": null, "summary": "A szerző frontend fejlesztőként elvesztette állását leépítés miatt és tanácsot kér.", "technologies": ["frontend"], "roles": ["frontend fejlesztő"], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar IT álláskereső a magyar munkaerőpiacon."}

Poszt: "Milyen monitort ajánlotok home office-hoz?"
Válasz: {"is_actual_layoff": false, "category": "other", "confidence": 0.95, "company": null, "sector": null, "headcount": null, "summary": "Monitor vásárlási tanács, nem kapcsolódik a munkaerőpiachoz.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": null}

Poszt: "Az Amazon 14 ezer embert küld el, akiket mesterséges intelligenciával fog pótolni"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.95, "company": "Amazon", "sector": "big tech", "headcount": 14000, "summary": "Az Amazon 14 ezer embert bocsát el, AI-val helyettesítve őket.", "technologies": ["AI"], "roles": [], "ai_role": "direct", "ai_context": "Az Amazon AI-val váltja ki az elbocsátott dolgozókat.", "hungarian_relevance": "none", "hungarian_context": null}

Poszt: "Leépítés van a Ubisoft torontói stúdiójában is, de a Splinter Cell remake készül tovább"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.9, "company": "Ubisoft", "sector": "entertainment", "headcount": null, "summary": "Leépítés az Ubisoft torontói stúdiójában.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "none", "hungarian_context": null}

Poszt: "Dr. Kulja András: Ma reggel kirúgták a feleségem édesanyját — eladóként dolgozott egy élelmiszerlánc boltjában"
Válasz: {"is_actual_layoff": false, "category": "other", "confidence": 0.95, "company": null, "sector": "other", "headcount": null, "summary": "Bolti eladó kirúgása egy élelmiszerlánc boltjából, nem IT pozíció.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyarországi eset, de nem IT pozíció."}

Poszt: "6000 fős leépítés jöhet a Heinekennél"
Válasz: {"is_actual_layoff": false, "category": "other", "confidence": 0.95, "company": "Heineken", "sector": "other", "headcount": 6000, "summary": "A Heineken gyári leépítése, nem IT szektor.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "none", "hungarian_context": null}

Poszt: "Leépítés jön a győri Audinál: ezzel indokolják a vezetők a döntést"
Válasz: {"is_actual_layoff": false, "category": "other", "confidence": 0.95, "company": "Audi", "sector": "automotive", "headcount": null, "summary": "Az Audi győri gyárában termelési leépítés, nem IT/fejlesztő pozíciókat érint.", "technologies": [], "roles": [], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar gyár, de gyári/termelési leépítés, nem IT pozíciók."}

Poszt: "Az Audi fejlesztőközpontja Győrben bezár, szoftvermérnökök érintettek"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.9, "company": "Audi", "sector": "automotive", "headcount": null, "summary": "Az Audi győri fejlesztőközpontjában szoftvermérnökök leépítése.", "technologies": [], "roles": ["szoftvermérnök"], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar fejlesztőközpont IT pozíciók leépítése."}

Poszt: "Magyar Posta elbocsát félszáz informatikust — túl sokat kerestek"
Válasz: {"is_actual_layoff": true, "category": "layoff", "confidence": 0.9, "company": "Magyar Posta", "sector": "government", "headcount": 50, "summary": "A Magyar Posta 50 informatikust bocsát el magas bérköltsége miatt.", "technologies": [], "roles": ["informatikus"], "ai_role": "none", "ai_context": null, "hungarian_relevance": "direct", "hungarian_context": "Magyar állami intézmény IT pozíciókat érintő leépítése."}

FONTOS A KARRIERTANÁCS/ÁLLÁSKERESŐ POSZTOKRÓL:
- Karriertanács, CV-tipp, "merre menjek", "megéri-e váltani", "hogyan keressek állást" típusú posztok NEM leépítési események → category: "other"
- Egyéni "kirúgtak és tanácsot kérek" poszt → category: "freeze" (ez rendben van, de NEM "layoff")
- "Junior álláskeresés perspektíva", "Milyen skilleket tanuljak?" → category: "other" (karriertanács, nem munkaerőpiaci esemény)

FONTOS A GENERIKUS AI/AUTOMATIZÁCIÓ CIKKEKRŐL:
- Ha egy cikk általánosságban beszél az AI munkaerőpiaci hatásáról (pl. "300 millió munkahely szűnik meg", "AI elveszi a munkát") de NEM nevez meg konkrét céget vagy eseményt → category: "other"
- CSAK akkor "layoff" vagy "anxiety" ha konkrét céget, helyszínt, vagy magyar IT munkaerőpiaci hatást említ
- Példák amik "other": "Goldman Sachs: 300 millió munkahely szűnhet meg az AI miatt", "Az automatizáció átalakítja a munkaerőpiacot"

FONTOS: Csak JSON-t válaszolj, semmi mást!"""


def _resolve_backend():
    """Resolve LLM backend config from env vars. Returns dict with url, headers, model, delay."""
    backend = os.environ.get('LLM_BACKEND', 'github').lower()

    if backend == 'openai':
        url = os.environ.get('LLM_API_URL', 'http://localhost:20128/v1/chat/completions')
        model = os.environ.get('LLM_MODEL', 'claude-3-haiku-20240307')
        return {
            'name': 'openai',
            'url': url,
            'headers': {'Content-Type': 'application/json'},
            'model': model,
            'delay': 0,
        }

    if backend == 'ollama':
        model = os.environ.get('LLM_MODEL', 'llama3.1')
        return {
            'name': 'ollama',
            'url': OLLAMA_API_URL,
            'headers': {'Content-Type': 'application/json'},
            'model': model,
            'delay': 0,
        }

    if backend == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        model = os.environ.get('LLM_MODEL', 'claude-3-haiku-20240307')
        return {
            'name': 'anthropic',
            'url': ANTHROPIC_API_URL,
            'headers': {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
            },
            'model': model,
            'delay': 0,
            'api_key': api_key,
        }

    # Default: github
    token = _resolve_token()
    model = os.environ.get('LLM_MODEL', 'gpt-4o-mini')
    return {
        'name': 'github',
        'url': GITHUB_API_URL,
        'headers': {
            'Authorization': f'Bearer {token}' if token else '',
            'Content-Type': 'application/json',
        },
        'model': model,
        'delay': 0.5,
        'token': token,
    }


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


def _check_ollama():
    """Check if Ollama is reachable. Returns True if available."""
    try:
        req = urllib.request.Request('http://localhost:11434/v1/models')
        urllib.request.urlopen(req, timeout=5)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return False


def _check_backend(backend):
    """Check if the LLM backend is available. Returns True if usable."""
    if backend['name'] == 'openai':
        # Generic OpenAI-compatible endpoint — try a quick health check
        try:
            from urllib.parse import urlparse
            parsed = urlparse(backend['url'])
            base = f'{parsed.scheme}://{parsed.netloc}/v1/models'
            req = urllib.request.Request(base)
            urllib.request.urlopen(req, timeout=5)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            print(f'\nLLM: OpenAI-compatible endpoint not reachable at {backend["url"]}')
            return False
        print(f'\nUsing OpenAI-compatible backend ({backend["url"]}, model: {backend["model"]})')
        return True
    if backend['name'] == 'ollama':
        if not _check_ollama():
            print('\nLLM: Ollama not reachable at localhost:11434')
            print('  Start Ollama: ollama serve')
            return False
        print(f'\nUsing Ollama backend (model: {backend["model"]})')
        return True
    elif backend['name'] == 'anthropic':
        if anthropic is None:
            print('\nLLM: anthropic package not installed')
            print('  pip install anthropic')
            return False
        if not backend.get('api_key'):
            print('\nLLM: no Anthropic API key available')
            print('  Set ANTHROPIC_API_KEY environment variable')
            return False
        # Quick SDK health check
        try:
            client = anthropic.Anthropic(api_key=backend['api_key'])
            client.models.list(limit=1)
            backend['_client'] = client  # reuse for later calls
        except anthropic.AuthenticationError:
            print('\nLLM: Anthropic API key is invalid')
            return False
        except anthropic.APIError:
            pass  # Non-auth errors are OK (e.g. model listing restricted)
        print(f'\nUsing Anthropic backend (model: {backend["model"]}, prompt caching enabled)')
        return True
    else:
        if not backend.get('token'):
            print('\nLLM: no GitHub token available')
            print('  Set GITHUB_TOKEN or install gh CLI')
            return False
        print(f'\nUsing GitHub Models backend (model: {backend["model"]})')
        return True


def _call_llm(backend, system_prompt, prompt, max_retries=5):
    """Call LLM API with exponential backoff. Returns parsed JSON dict or None."""
    if backend['name'] == 'anthropic':
        return _call_llm_anthropic(backend, system_prompt, prompt, max_retries)

    # OpenAI-compatible backends (ollama, github, openai)
    body_dict = {
        'model': backend['model'],
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.1,
        'stream': False,
    }
    # JSON mode: different param for Ollama vs OpenAI
    if backend['name'] == 'ollama':
        body_dict['format'] = 'json'
    elif backend['name'] != 'openai':
        body_dict['response_format'] = {'type': 'json_object'}

    body = json.dumps(body_dict).encode()

    for attempt in range(max_retries):
        req = urllib.request.Request(
            backend['url'],
            data=body,
            headers=backend['headers'],
        )

        try:
            resp = urllib.request.urlopen(req, timeout=120)
            data = json.loads(resp.read())
            content = data['choices'][0]['message']['content']
            # Strip markdown code fences (```json ... ```) if present
            content = re.sub(r'^```(?:json)?\s*\n?', '', content.strip())
            content = re.sub(r'\n?```\s*$', '', content.strip())
            return json.loads(content)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                delay = 10 * (2 ** attempt)
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


def _call_llm_anthropic(backend, system_prompt, prompt, max_retries=5):
    """Call Anthropic API via SDK with prompt caching. Returns parsed JSON dict or None."""
    client = backend.get('_client')
    if client is None:
        client = anthropic.Anthropic(api_key=backend['api_key'])
        backend['_client'] = client

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=backend['model'],
                max_tokens=1024,
                temperature=0.1,
                system=[{
                    'type': 'text',
                    'text': system_prompt,
                    'cache_control': {'type': 'ephemeral'},
                }],
                messages=[{'role': 'user', 'content': prompt}],
            )
            content = response.content[0].text
            # Strip markdown code fences if present
            content = re.sub(r'^```(?:json)?\s*\n?', '', content.strip())
            content = re.sub(r'\n?```\s*$', '', content.strip())
            # Log cache stats on first call
            usage = response.usage
            cache_read = getattr(usage, 'cache_read_input_tokens', 0) or 0
            cache_create = getattr(usage, 'cache_creation_input_tokens', 0) or 0
            if cache_read > 0 or cache_create > 0:
                if not backend.get('_cache_logged'):
                    print(f'    [cache] read={cache_read}, created={cache_create}')
                    backend['_cache_logged'] = True
            return json.loads(content)
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                delay = 10 * (2 ** attempt)
                print(f'    Rate limited, waiting {delay}s (attempt {attempt+1}/{max_retries})...')
                time.sleep(delay)
                continue
            print('    Rate limit exceeded after retries')
            return None
        except anthropic.APIError as e:
            print(f'    Anthropic API error: {e}')
            return None
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f'    Parse error: {e}')
            return None


def _map_relevance(llm_result):
    """Map LLM result to relevance 0-3 using category and hungarian_relevance."""
    hungarian = llm_result.get('hungarian_relevance', 'direct')

    # Non-Hungarian posts get 0 relevance
    if hungarian == 'none':
        return 0

    category = llm_result.get('category')
    confidence = llm_result.get('confidence', 0.0)

    if category:
        if category == 'layoff' and confidence >= 0.7:
            base = 3
        elif category == 'layoff':
            base = 2
        elif category == 'freeze':
            base = 2
        elif category == 'anxiety':
            base = 1
        else:
            base = 0
    else:
        # Fallback for old data without category
        is_layoff = llm_result.get('is_actual_layoff', False)
        if is_layoff and confidence >= 0.8:
            base = 3
        elif is_layoff and confidence >= 0.5:
            base = 2
        elif not is_layoff and confidence < 0.7:
            base = 1
        else:
            base = 0

    # Indirect Hungarian relevance: cap at 2
    if hungarian == 'indirect' and base > 2:
        base = 2

    return base


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


def batch_triage(posts, backend=None, batch_size=50, frozen_ids=None):
    """Batch triage: LLM calls to filter relevant posts by title.

    Splits posts into batches (default 50) to stay within LLM context limits.
    Returns dict {post_id: True/False} or None if all LLM calls fail.

    Args:
        frozen_ids: set of post IDs to skip (already frozen/validated).
    """
    if frozen_ids is None:
        frozen_ids = set()

    # Filter out frozen posts before triage
    posts_to_triage = [p for p in posts if p.get('id', '') not in frozen_ids]
    skipped = len(posts) - len(posts_to_triage)

    if backend is None:
        backend = _resolve_backend()

    if not _check_backend(backend):
        print('  Batch triage SKIPPED — no LLM available')
        return None

    if skipped > 0:
        print(f'\nBatch triage: {len(posts_to_triage)} poszt ({skipped} frozen skipped), {batch_size}-es batch-ekben...')
    else:
        print(f'\nBatch triage: {len(posts_to_triage)} poszt címének szűrése ({batch_size}-es batch-ekben)...')

    # Use filtered list for triage
    posts = posts_to_triage

    all_relevant_global_indices = set()
    total_batches = (len(posts) + batch_size - 1) // batch_size
    errors = 0

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(posts))
        batch = posts[start:end]

        # Build numbered title list (1-based within batch)
        numbered_titles = []
        for i, post in enumerate(batch):
            title = post.get('title', '').strip()
            subreddit = post.get('subreddit', '')
            numbered_titles.append(f'{i+1}. [r/{subreddit}] {title}')

        prompt = '\n'.join(numbered_titles)
        print(f'  Batch {batch_idx+1}/{total_batches} ({len(batch)} poszt)...', end=' ')

        if backend['delay'] > 0:
            time.sleep(backend['delay'])

        result = _call_llm(backend, TRIAGE_SYSTEM_PROMPT, prompt)

        if result is None:
            print('FAILED')
            errors += 1
            continue

        relevant_indices = result.get('relevant', [])

        # Map batch-local indices back to global indices
        for idx in relevant_indices:
            if isinstance(idx, int) and 1 <= idx <= len(batch):
                all_relevant_global_indices.add(start + idx)  # 1-based to global 1-based

        relevant_in_batch = len([i for i in relevant_indices if isinstance(i, int) and 1 <= i <= len(batch)])
        print(f'{relevant_in_batch}/{len(batch)} releváns')

    if errors == total_batches:
        print('  Összes batch FAILED — falling back to keyword filter')
        return None

    # Build result dict
    triage_results = {}
    for i, post in enumerate(posts):
        post_id = post.get('id', str(i))
        triage_results[post_id] = (i + 1) in all_relevant_global_indices

    relevant_count = sum(1 for v in triage_results.values() if v)
    print(f'  Batch triage összesítés: {relevant_count}/{len(posts)} releváns ({relevant_count*100//len(posts)}%)')

    return triage_results


def validate_posts(posts, triage_results=None, frozen_ids=None):
    """Validate analyzed posts with LLM. Returns enriched post list + stats dict.

    Args:
        posts: List of analyzed post dicts.
        triage_results: Optional dict {post_id: bool} from batch_triage().
                       If provided, only posts with True are validated.
                       If None, falls back to keyword-based relevance >= 1 filter.
        frozen_ids: set of post IDs to skip (already frozen/validated).
    """
    if frozen_ids is None:
        frozen_ids = set()

    # Remove frozen posts from processing
    fresh_posts = [p for p in posts if p.get('id', '') not in frozen_ids]
    frozen_skipped = len(posts) - len(fresh_posts)
    if frozen_skipped > 0:
        print(f'  Skipping {frozen_skipped} frozen posts')
    posts = fresh_posts
    backend = _resolve_backend()

    stats = {
        'validated': 0,
        'errors': 0,
        'skipped': 0,
        'triage_used': triage_results is not None,
        'backend_name': backend['name'],
        'est_input_tokens': 0,
        'est_output_tokens': 0,
        'est_manual_hours': 0.0,
        'elapsed_seconds': 0.0,
    }

    # Check backend availability
    if not _check_backend(backend):
        print('LLM validation: SKIPPED')
        for post in posts:
            post['llm_validated'] = False
        stats['skipped'] = len(posts)
        stats['est_manual_hours'] = sum(_estimate_manual_minutes(p) for p in posts) / 60
        return posts, stats

    # Filter posts to validate: union of triage + keyword
    if triage_results is not None:
        # Union: relevant if triage says yes OR keyword relevance >= 1
        def _is_relevant(p):
            triage_yes = triage_results.get(p.get('id', ''), False)
            keyword_yes = p.get('relevance', 0) >= 1
            return triage_yes or keyword_yes
        to_validate = [p for p in posts if _is_relevant(p)]
        skip = [p for p in posts if not _is_relevant(p)]
        filter_label = 'triage + keyword union'
    else:
        # Fallback: keyword-based relevance >= 1
        to_validate = [p for p in posts if p.get('relevance', 0) >= 1]
        skip = [p for p in posts if p.get('relevance', 0) < 1]
        filter_label = 'keyword relevance >= 1'

    # Mark triage_relevant on all posts
    validate_ids = set(p.get('id', '') for p in to_validate)
    for p in posts:
        p['triage_relevant'] = p.get('id', '') in validate_ids

    for p in skip:
        p['llm_validated'] = False
    stats['skipped'] = len(skip)

    print(f'LLM validation: {len(to_validate)} posts to validate via {filter_label} (skipping {len(skip)})')

    start_time = time.time()

    for i, post in enumerate(to_validate):
        if post.get('llm_validated') and 'llm_sector' in post and 'llm_hungarian_relevance' in post and 'llm_event_label' in post:
            stats['validated'] += 1
            continue

        print(f'  [{i+1}/{len(to_validate)}] {post["title"][:50]}...')

        prompt = _build_prompt(post)

        # Estimate tokens (Hungarian text ≈ 1 token per 3 chars)
        est_input = (len(SYSTEM_PROMPT) + len(prompt)) / 3
        stats['est_input_tokens'] += int(est_input)

        if backend['delay'] > 0:
            time.sleep(backend['delay'])

        result = _call_llm(backend, SYSTEM_PROMPT, prompt)

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
        post['llm_category'] = result.get('category', 'other')
        post['llm_company'] = result.get('company')
        post['llm_sector'] = result.get('sector')
        post['llm_headcount'] = result.get('headcount')
        post['llm_confidence'] = result.get('confidence', 0.0)
        post['llm_summary'] = result.get('summary', '')
        post['llm_technologies'] = result.get('technologies', [])
        post['llm_roles'] = result.get('roles', [])
        post['llm_ai_role'] = result.get('ai_role', 'none')
        post['llm_ai_context'] = result.get('ai_context')
        post['llm_hungarian_relevance'] = result.get('hungarian_relevance', 'direct')
        post['llm_hungarian_context'] = result.get('hungarian_context')
        post['llm_event_label'] = result.get('event_label')
        stats['validated'] += 1

    stats['elapsed_seconds'] = time.time() - start_time
    stats['est_manual_hours'] = sum(_estimate_manual_minutes(p) for p in posts) / 60

    # Cost estimation (per-million-token rates)
    if backend['name'] == 'anthropic':
        input_rate = 0.80   # Haiku 4.5
        output_rate = 4.00
    else:
        input_rate = 0.15   # gpt-4o-mini
        output_rate = 0.60
    est_input_cost = stats['est_input_tokens'] / 1_000_000 * input_rate
    est_output_cost = stats['est_output_tokens'] / 1_000_000 * output_rate
    est_total_cost = est_input_cost + est_output_cost

    print(f'\nLLM validation complete:')
    print(f'  Backend: {backend["name"]} ({backend["model"]})')
    print(f'  Filter: {filter_label}')
    print(f'  Validated: {stats["validated"]}')
    print(f'  Errors: {stats["errors"]}')
    print(f'  Skipped: {stats["skipped"]}')
    print(f'  Time: {stats["elapsed_seconds"]:.0f}s')
    print(f'  Est. tokens: ~{stats["est_input_tokens"]:,} input + ~{stats["est_output_tokens"]:,} output')
    if backend['name'] in ('ollama', 'openai'):
        print(f'  Cost: $0.00 (local)')
    elif backend['name'] == 'anthropic':
        print(f'  Est. cost (Haiku rates): ${est_total_cost:.3f}')
    else:
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
