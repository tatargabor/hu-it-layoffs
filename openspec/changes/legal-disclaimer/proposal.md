## Why

A projekt cégneveket említ leépítési kontextusban (Ericsson, OTP, Lensa, stb.) publikus Reddit posztok alapján. Jogi védelem kell: nem saját állítás, harmadik fél tartalma, nem ellenőrzött, eltávolítási lehetőség.

## What Changes

- Jogi nyilatkozat (disclaimer) a markdown report elejére
- Ugyanez a HTML dashboard-ba (footer + header között)
- LICENSE fájl disclaimer szekció
- Kontakt/eltávolítási lehetőség jelzése

## Capabilities

### New Capabilities
- `legal-disclaimer`: Jogi nyilatkozat szöveg generálása és elhelyezése a report, dashboard és repo szintjén

### Modified Capabilities

## Impact

- `src/report.py`: Disclaimer szekció a report elejére
- `src/visualize.py`: Disclaimer a dashboard footerbe
- `README.md`: Disclaimer látható a repo főoldalán
