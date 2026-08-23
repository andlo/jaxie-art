# Jaxie's Drawings

En online samling af tegninger, sorteret efter år / uge / dag.
Password-beskyttet statisk galleri hostet med Cloudflare Pages.

## Sådan tilføjer du nye tegninger

1. Læg billedfilerne i `images/ÅÅÅÅ/MM/DD/` — f.eks. `images/2026/08/22/tegning1.png`
   (opret mapperne hvis de ikke findes). Nemmeste vej: naviger direkte til
   `github.com/andlo/jaxie-art/upload/master/images/ÅÅÅÅ/MM/DD` og træk
   filer ind — ingen kloning nødvendig.
2. `git push` (eller commit direkte i browseren) — en GitHub Action bygger
   automatisk `manifest.json` og deployer til Cloudflare Pages.

## Struktur

```
images/2026/08/22/*.png       ← selve tegningerne, organiseret efter dato
scripts/build_manifest.py     ← scanner images/ og bygger manifest.json
manifest.json                  ← genereret data siden bruger (byg ikke i hånden)
index.html / assets/           ← selve galleri-siden
functions/_middleware.js       ← password-gate (Cloudflare Pages Functions)
```

## Fjernelse af et billede

Klik "Request removal" i galleriet — opretter et GitHub-issue, der enten
fjerner billedet automatisk (hvis du opretter det) eller kræver, at du
tilføjer labelet "approved" (hvis nogen andre gør).

## Licens

Tegningerne er udgivet under **CC BY-NC-ND 4.0** (se `LICENSE`).
Koden til selve galleri-siden må frit genbruges (se `LICENSE-CODE`).
