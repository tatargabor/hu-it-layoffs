## MODIFIED Requirements

### Requirement: Batch triage bővebb szűrés

A batch triage SHALL bővebben szűrjön mint a korábbi keyword filter — a cél hogy ne veszítsünk el releváns posztokat. Inkább legyen false positive (amit a full validation majd kiszűr) mint false negative.

A `TRIAGE_SYSTEM_PROMPT` SHALL tartalmazzon explicit "NEM releváns" példákat a fizikai kiskereskedelmi és gyári munkás leépítésekre:
- "Barkácsáruház (OBI), elektronikai bolt (BestByte), szupermarket (Tesco, Aldi) leépítés = NEM releváns, KIVÉVE ha kifejezetten IT pozíciókat említ"
- "Autógyári fizikai munkás, akkugyári dolgozó, targoncás leépítés = NEM releváns, KIVÉVE ha szoftvermérnök/fejlesztő érintett"
- "Kórházi, egyetemi, operaházi, TV csatornai leépítés = NEM releváns, KIVÉVE ha IT pozíciókat említ"

#### Scenario: OBI barkácsáruház leépítés nem releváns
- **WHEN** a címek között szerepel "Az OBI elismerte: fű alatt nagy leépítést hajtott végre"
- **THEN** a poszt sorszáma NEM jelenik meg a releváns listában

#### Scenario: BestByte boltzárás nem releváns
- **WHEN** a címek között szerepel "Szerkezetátalakítás alatt a BestByte: boltzárások és leépítés"
- **THEN** a poszt sorszáma NEM jelenik meg a releváns listában

#### Scenario: Audi gyári munkás nem releváns
- **WHEN** a címek között szerepel "Leépítés jön a győri Audinál" (és a cím nem említ IT pozíciókat)
- **THEN** a poszt sorszáma NEM jelenik meg a releváns listában

#### Scenario: Audi fejlesztőközpont releváns
- **WHEN** a címek között szerepel "Az Audi fejlesztőközpontja Győrben bezár, szoftvermérnökök érintettek"
- **THEN** a poszt sorszáma megjelenik a releváns listában

#### Scenario: IT leépítés továbbra is releváns
- **WHEN** a címek között szerepel "Ericsson 200 embert bocsát el Budapesten"
- **THEN** a poszt sorszáma megjelenik a releváns listában

#### Scenario: Implicit freeze jel továbbra is releváns
- **WHEN** a cím "Az IT fejvadászok hogy nem halnak éhen??"
- **THEN** a poszt relevánsként jelölve (implicit piac-lassulás jel)
