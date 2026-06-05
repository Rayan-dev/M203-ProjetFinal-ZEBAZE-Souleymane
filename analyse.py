"""
Mini-analyse SQL — lancer après : scrapy crawl hockey
"""
import sqlite3

con = sqlite3.connect("hockey.db")
cur = con.cursor()

print("\n" + "="*55)
print("  PALMARÈS NHL")
print("="*55)

count = cur.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
print(f"\nÉquipes-saisons collectées : {count}")

seasons = cur.execute("SELECT MIN(year), MAX(year) FROM teams").fetchone()
print(f"Période couverte           : {seasons[0]} → {seasons[1]}")

print("\nTop 5 meilleurs win_pct :")
for r in cur.execute("SELECT name,year,win_pct,wins,losses FROM teams ORDER BY win_pct DESC LIMIT 5"):
    print(f"  {r[1]} | {r[0]:<35} | {r[2]:.3f} | {r[3]}W {r[4]}L")

avg = cur.execute("SELECT ROUND(AVG(goals_for),1) FROM teams").fetchone()[0]
print(f"\nMoyenne buts pour : {avg}")

try:
    eras = cur.execute("SELECT era, COUNT(*) FROM teams WHERE era IS NOT NULL GROUP BY era ORDER BY 2 DESC").fetchall()
    if eras:
        print("\nEnrichissement LLM — ères NHL :")
        for era, n in eras:
            print(f"  {era:<20} : {n} équipes-saisons")
except Exception:
    pass

print("\n" + "="*55)
print("  OSCARS (bonus AJAX)")
print("="*55)
try:
    ocount = cur.execute("SELECT COUNT(*) FROM oscars").fetchone()[0]
    print(f"\nFilms collectés : {ocount}")
    print("\nTop 3 films (awards) :")
    for r in cur.execute("SELECT title,year,awards,nominations FROM oscars ORDER BY awards DESC LIMIT 3"):
        print(f"  {r[1]} | {r[0]:<40} | {r[2]} awards / {r[3]} noms")
    print("\nFilms par année :")
    for r in cur.execute("SELECT year, COUNT(*) FROM oscars GROUP BY year ORDER BY year"):
        print(f"  {r[0]} : {r[1]} films")
except Exception:
    print("  (lancer d'abord : scrapy crawl oscars)")

con.close()
