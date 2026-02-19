## Context

A HTML dashboard (`src/visualize.py`) ékezet nélküli magyar szöveget generál (Python f-string-ekben ASCII karakterek). A dashboard nem tartalmaz megosztási elemeket, meta tageket, vagy branding-et. A site GitHub Pages-en lesz hosztolva.

## Goals / Non-Goals

**Goals:**
- Helyes magyar ékezetek mindenhol a HTML-ben
- "magyar.dev/layoffs" brand identitás
- Social media megosztás gombok (zero JS dependency)
- GitHub Watch gomb feliratkozáshoz
- Open Graph meta tagek a link preview-hoz

**Non-Goals:**
- Saját domain vásárlás (egyelőre GitHub Pages URL)
- Email newsletter service integráció (GitHub Watch elég)
- Favicon tervezés (emoji vagy egyszerű SVG)
- Analytics / tracking

## Decisions

### D1: Feliratkozás = GitHub Watch

Nincs szükség email service-re. A GitHub repo "Watch" funkciója pontosan azt csinálja amit akarunk — notification (email) minden commit-ra. Egy "Watch on GitHub" gomb a headerben elég, ami a repo URL-re linkel `#notifications` anchor-rel.

### D2: Share gombok — sima URL-ek, zero JS

Minden social platform támogatja az URL-alapú megosztást:
- Twitter: `https://twitter.com/intent/tweet?text=...&url=...`
- LinkedIn: `https://www.linkedin.com/sharing/share-offsite/?url=...`
- Facebook: `https://www.facebook.com/sharer/sharer.php?u=...`
- Copy link: `navigator.clipboard.writeText()` — ez az egyetlen sor JS

### D3: Open Graph meta tagek

```html
<meta property="og:title" content="magyar.dev/layoffs — IT Leépítés Radar">
<meta property="og:description" content="Magyar IT szektor leépítések ...">
<meta property="og:type" content="website">
<meta property="og:url" content="https://...github.io/reddit/">
<meta name="twitter:card" content="summary_large_image">
```

Az `og:image`-hez nincs külön kép — a `summary` twitter card elég, vagy generálhatunk egy egyszerű SVG-t a statokkal.

### D4: Ékezetek — közvetlen javítás

Az f-string-ekben a szövegek egyszerűen kicserélendők. A HTML `<meta charset="UTF-8">` már van, tehát az ékezetek probléma nélkül megjelennek.

### D5: Branding layout

```
┌──────────────────────────────────────────────────┐
│  magyar.dev/layoffs                              │
│  IT Leépítés Radar                               │
│                                                  │
│  1 óra tervezés, 2 óra generálás                 │
│                                                  │
│  [Watch on GitHub] [Share ▼]                     │
├──────────────────────────────────────────────────┤
│  ... stat cards, charts, tables ...              │
├──────────────────────────────────────────────────┤
│  powered by Claude Code · OpenSpec · Agentic     │
│  Adatok: Reddit publikus API                     │
└──────────────────────────────────────────────────┘
```

## Risks / Trade-offs

**[GitHub Pages URL nem magyar.dev/layoffs]** → Egyelőre `username.github.io/reddit/`. Custom domain később konfigurálható GitHub Pages settings-ben. A branding szöveg akkor is "magyar.dev/layoffs" marad mint név, a tényleges URL ettől független.

**[Share gomb copy link — clipboard API]** → Nem minden böngészőben működik (régi mobilok). Fallback: a link megjelenik egy text input-ban amit manuálisan ki lehet másolni.
