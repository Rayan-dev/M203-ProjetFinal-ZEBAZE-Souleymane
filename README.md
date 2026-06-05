# M203 · Projet Final — Sujet 2 · Palmarès NHL + Oscars AJAX

**Groupe :** ZEBAZE Rayan · SOULEYMANE [Prénom]  
**Repo :** https://github.com/Rayan-dev/M203-ProjetFinal-ZEBAZE-Souleymane  
**Cible principale :** `https://www.scrapethissite.com/pages/forms/`  
**Bonus AJAX :** `https://www.scrapethissite.com/pages/ajax-javascript/`  
**Bonus LLM :** enrichissement ère NHL via Claude API

---

## Installation et lancement

### 1. Prérequis — installer uv (une seule fois)
```powershell
pip install uv
```

### 2. Cloner le projet
```powershell
git clone https://github.com/Rayan-dev/M203-ProjetFinal-ZEBAZE-Souleymane.git
cd M203-ProjetFinal-ZEBAZE-Souleymane
```

### 3. Installer les dépendances
```powershell
uv sync
.venv\Scripts\activate
```

### 4. Lancer les crawls
```powershell
# Collecte complète (~580 équipes-saisons)
scrapy crawl hockey

# Filtre formulaire — équipes Boston uniquement
scrapy crawl hockey -a team="Boston"

# Filtre par saison
scrapy crawl hockey -a year="1998"

# Bonus AJAX Oscars 2010–2015
scrapy crawl oscars

# Analyse après collecte
python analyse.py
```

### 5. Bonus LLM (optionnel)
```powershell
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
scrapy crawl hockey
```

### Sorties
| Fichier | Contenu |
|---|---|
| `hockey.db` | SQLite — table `teams` (idempotence avec ON CONFLICT) |
| `hockey_teams.json` | Export JSON équipes (582 items) |
| `oscars.json` | Export JSON films (87 items) |

---

## Décisions défendues

### Quel barreau et pourquoi pas celui du dessus ?

**Scrapy — barreau 3**

Recon avant tout code :
- `view-source` : données dans le HTML statique → httpx+BS4 suffirait techniquement
- DevTools > Network : aucune API JSON sur `/forms/` → Playwright inutile
- Volume ~580 items + pagination + formulaire + retries → Scrapy se justifie

Pourquoi pas Playwright ? Aucun JS à rendre. Surcoût 10× pour rien.  
Pourquoi pas httpx+BS4 seul ? On recoderait manuellement retries, scheduler, 
export, politesse = recoder la moitié de Scrapy.

### Bonus Oscars : barreau 1 (API cachée)

DevTools révèle `?ajax=true&year=YYYY` → JSON pur.  
On appelle l'endpoint directement. Monter au barreau 2 ou 3 ici serait une erreur de diagnostic.

### Bonus LLM : ère NHL

Claude Haiku catégorise chaque équipe-saison : *Original Six*, *Expansion Era*, *Modern Era*.  
Validation systématique : sortie hors liste connue → `"Unknown"`. Jamais en aveugle.  
Pipeline désactivé si `ANTHROPIC_API_KEY` absent → le projet tourne sans clé.

### Clé primaire

- `teams` : `(name, year)` — une franchise sur plusieurs saisons
- `oscars` : `(title, year)` — sécurité si film nominé plusieurs fois
- `name` seul écarté : écraserait toutes les saisons sauf la dernière

### Politesse & résilience

| Paramètre | Valeur | Raison |
|---|---|---|
| `DOWNLOAD_DELAY` | 1 s | Plancher partagé par toute la promo |
| `AUTOTHROTTLE` | activé | S'adapte à la latence réelle |
| `RETRY_TIMES` | 3 | Couvre les erreurs transitoires |
| `RETRY_HTTP_CODES` | 429, 5xx | Rate-limit + serveur KO |
| `DOWNLOAD_TIMEOUT` | 20 s | Évite les blocages infinis |

### robots.txt

```
User-agent: *
Disallow:
```
Tout autorisé. `ROBOTSTXT_OBEY=True` conservé par principe.

### RGPD

Bac à sable pédagogique — statistiques sportives anonymisées, aucune donnée personnelle.  
En contexte réel : vérifier base légale, durée de conservation, droit à l'effacement.

### Alternatives écartées

| Outil | Raison |
|---|---|
| Playwright | Pas de JS à rendre |
| httpx+BS4 seul | Viable mais gestion manuelle à ce volume |
| Selenium | Obsolète, plus lent que Playwright |

---

## Réponses jury

**Structure qui casse si le site change ?**  
Sélecteurs CSS isolés dans `hockey_spider.py` — un seul fichier à mettre à jour.

**Pas de doublons ?**  
`ON CONFLICT(name,year) DO UPDATE` au niveau SQL.  
Preuve : lancer 2× → `SELECT COUNT(*) FROM teams` identique.

**Pourquoi Scrapy ?**  
Volume + pagination + retries + politesse + export = les deux critères exacts qui le justifient.
