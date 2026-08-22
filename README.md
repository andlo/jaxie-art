# Sonias tegninger

En online samling af Sonias MS Paint-tegninger, sorteret efter år / uge / dag.
Statisk galleri hostet med GitHub Pages.

## Sådan tilføjer du nye tegninger

1. Læg billedfilerne i `images/ÅÅÅÅ/MM/DD/` — f.eks. `images/2026/08/22/tegning1.png`
   (opret mapperne hvis de ikke findes).
2. Kør `python3 scripts/build_manifest.py` — det scanner `images/` og
   genererer `manifest.json` som siden bruger.
3. `git add . && git commit -m "Nye tegninger" && git push`

GitHub Actions kører automatisk `build_manifest.py` og deployer til
GitHub Pages ved hvert push til `main` — så du behøver reelt kun at
lægge billeder i de rigtige mapper og pushe. Trin 2 er kun nødvendigt
hvis du vil se resultatet lokalt først (`python3 -m http.server` i
repo-mappen og åbn `http://localhost:8000`).

## Struktur

```
images/2026/08/22/*.png    ← selve tegningerne, organiseret efter dato
scripts/build_manifest.py  ← scanner images/ og bygger manifest.json
manifest.json               ← genereret data siden bruger (byg ikke i hånden)
index.html / assets/        ← selve galleri-siden
```

## Licens

Tegningerne er udgivet under **CC BY-NC-ND 4.0** (se `LICENSE`) —
andre må se og dele dem med kredit, men ikke ændre dem eller bruge dem
kommercielt. Koden til selve galleri-siden må frit genbruges (MIT-agtig,
se `LICENSE-CODE`).
