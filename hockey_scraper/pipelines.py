"""
Pipelines — 3 responsabilités séparées :
  100 · NormalisePipeline  — str → int / float / bool / None
  150 · LLMEnrichPipeline  — bonus : catégorise l'ère NHL via Claude API
  200 · SQLitePipeline     — stockage idempotent (UPSERT)
"""
import os
import sqlite3

import anthropic
from itemadapter import ItemAdapter


class NormalisePipeline:
    """Convertit les champs bruts HTML en types Python corrects."""

    def process_item(self, item, spider):
        a = ItemAdapter(item)

        if "win_pct" in a.field_names():        # HockeyTeamItem
            a["year"]          = self._int(a.get("year"))
            a["wins"]          = self._int(a.get("wins"))
            a["losses"]        = self._int(a.get("losses"))
            a["ot_losses"]     = self._int(a.get("ot_losses"))  # None si vide
            a["win_pct"]       = self._float(a.get("win_pct"))
            a["goals_for"]     = self._int(a.get("goals_for"))
            a["goals_against"] = self._int(a.get("goals_against"))

        if "awards" in a.field_names():         # OscarFilmItem
            a["year"]         = self._int(a.get("year"))
            a["awards"]       = self._int(a.get("awards"))
            a["nominations"]  = self._int(a.get("nominations"))
            a["best_picture"] = bool(a.get("best_picture"))

        return item

    @staticmethod
    def _int(v):
        s = str(v).strip() if v is not None else ""
        return int(s) if s else None

    @staticmethod
    def _float(v):
        s = str(v).strip() if v is not None else ""
        return float(s) if s else None


class LLMEnrichPipeline:
    """
    Bonus LLM — classe chaque équipe dans une ère NHL via Claude Haiku.
    Désactivé silencieusement si ANTHROPIC_API_KEY est absent.
    Validation systématique : on n'accepte que les valeurs connues.
    """

    VALID_ERAS = {"Original Six", "Expansion Era", "Modern Era"}

    def open_spider(self, spider):
        key = os.environ.get("ANTHROPIC_API_KEY")
        self.enabled = bool(key)
        if self.enabled:
            self.client = anthropic.Anthropic(api_key=key)
            spider.logger.info("LLMEnrichPipeline activé.")
        else:
            spider.logger.warning("LLMEnrichPipeline désactivé — ANTHROPIC_API_KEY absent.")

    def process_item(self, item, spider):
        if not self.enabled:
            return item
        a = ItemAdapter(item)
        if "win_pct" not in a.field_names():
            return item

        try:
            resp = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=20,
                messages=[{"role": "user", "content": (
                    f"NHL team '{a.get('name')}', season {a.get('year')}. "
                    f"Classify into exactly one of: "
                    f"'Original Six', 'Expansion Era', 'Modern Era'. "
                    f"Reply with ONLY the category name, nothing else."
                )}],
            )
            raw = resp.content[0].text.strip()
            a["era"] = raw if raw in self.VALID_ERAS else "Unknown"
        except Exception as e:
            spider.logger.warning(f"LLM error: {e}")
            a["era"] = "Unknown"

        return item


class SQLitePipeline:
    """
    Stockage idempotent.
    Clé primaire teams : (name, year) — une franchise sur plusieurs saisons.
    Clé primaire oscars : (title, year).
    UPSERT → relancer le crawl ne crée jamais de doublons.
    """

    def open_spider(self, spider):
        self.con = sqlite3.connect("hockey.db")
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                name TEXT NOT NULL, year INTEGER NOT NULL,
                wins INTEGER, losses INTEGER, ot_losses INTEGER,
                win_pct REAL, goals_for INTEGER, goals_against INTEGER,
                era TEXT,
                PRIMARY KEY (name, year)
            )""")
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS oscars (
                title TEXT NOT NULL, year INTEGER NOT NULL,
                awards INTEGER, nominations INTEGER, best_picture INTEGER,
                PRIMARY KEY (title, year)
            )""")
        self.con.commit()

    def close_spider(self, spider):
        self.con.close()

    def process_item(self, item, spider):
        a = ItemAdapter(item)

        if "win_pct" in a.field_names():
            self.con.execute("""
                INSERT INTO teams
                    (name,year,wins,losses,ot_losses,win_pct,goals_for,goals_against,era)
                VALUES (:name,:year,:wins,:losses,:ot_losses,:win_pct,:goals_for,:goals_against,:era)
                ON CONFLICT(name,year) DO UPDATE SET
                    wins=excluded.wins, losses=excluded.losses,
                    ot_losses=excluded.ot_losses, win_pct=excluded.win_pct,
                    goals_for=excluded.goals_for, goals_against=excluded.goals_against,
                    era=excluded.era
            """, {**dict(a), "era": a.get("era")})

        elif "awards" in a.field_names():
            self.con.execute("""
                INSERT INTO oscars (title,year,awards,nominations,best_picture)
                VALUES (:title,:year,:awards,:nominations,:best_picture)
                ON CONFLICT(title,year) DO UPDATE SET
                    awards=excluded.awards, nominations=excluded.nominations,
                    best_picture=excluded.best_picture
            """, dict(a))

        self.con.commit()
        return item
