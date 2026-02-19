## Why

A dashboard jelenleg névtelen, ékezet nélküli szöveget tartalmaz, és nincs megosztási lehetőség. Ahhoz hogy a riport terjedjen és hasznos legyen a közösségnek, kell egy felismerhető brand, helyes magyar ékezetek, social media megosztás, és feliratkozási lehetőség.

## What Changes

- Branding: "magyar.dev/layoffs" név, tagline: "1 óra tervezés, 2 óra generálás", footer: "powered by Claude Code + OpenSpec + Agentic"
- Ékezet fix: az összes ékezet nélküli szöveg javítása a HTML dashboardban (Leepitesek → Leépítések, Kozvetlen → Közvetlen, stb.)
- Open Graph meta tagek a szép link preview-hoz (Twitter Card, Facebook OG, LinkedIn)
- Social media share gombok: Twitter/X, LinkedIn, Facebook, Copy link
- GitHub Watch gomb feliratkozáshoz (repo notification = email ha új report commitolódik)
- Megosztható anchored linkek a report szekcióihoz

## Capabilities

### New Capabilities
- `social-sharing`: Share gombok (Twitter/X, LinkedIn, Facebook, Copy link), Open Graph meta tagek, anchor linkek a szekciókhoz
- `branding`: "magyar.dev/layoffs" név, tagline, powered-by footer, favicon, konzisztens vizuális identitás

### Modified Capabilities
- `html-visualizer`: Ékezet fix minden szövegben, GitHub Watch gomb a headerben, branding elemek integrálása, share gombok elhelyezése

## Impact

- Módosított fájlok: `src/visualize.py` (ékezetek, branding, share gombok, OG tagek)
- Nincs új dependency (share linkek sima URL-ek, OG tagek meta tagek, Watch gomb GitHub link)
- GitHub Pages URL lesz a megosztott link (pl. `username.github.io/reddit/`)
