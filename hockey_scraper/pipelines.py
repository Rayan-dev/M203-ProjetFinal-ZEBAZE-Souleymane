import os
import sqlite3
from itemadapter import ItemAdapter
import anthropic


# ─────────────────────────────────────────────
# 1. NORMALISATION
# ─────────────────────────────────────────────
class NormalisePipeline:
    """Convertit les champs string → int / float proprement."""

    def process_item(self, item, spider):
        a = ItemAdapter(item)

        # 👉 Hockey items
        if a.get("win_pct") is not None:

            a["year"] = self._int(a.get("year"))
            a["wins"] = self._int(a.get("wins"))
            a["losses"] = self._int(a.get("losses"))
            a["ot_losses"] = self._int(a.get("ot_losses"))
            a["win_pct"] = self._float(a.get("win_pct"))
            a["goals_for"] = self._int(a.get("goals_for"))
            a["goals_against"] = self._int(a.get("goals_against"))

        # 👉 Oscars items
        if a.get("awards") is not None:

            a["year"] = self._int(a.get("year"))
            a["awards"] = self._int(a.get("awards"))
            a["nominations"] = self._int(a.get("nominations"))
            a["best_picture"] = bool(a.get("best_picture"))

        return item

    @staticmethod
    def _int(v):
        try:
            return int(str(v).strip())
        except:
            return None

    @staticmethod
    def _float(v):
        try:
            return float(str(v).strip())
        except:
            return None


# ─────────────────────────────────────────────
# 2. LLM ENRICH (OPTIONNEL)
# ─────────────────────────────────────────────
class LLMEnrichPipeline:
    """Ajoute une classification d’ère NHL via Claude (optionnel)."""

    VALID_ERAS = {"Original Six", "Expansion Era", "Modern Era"}

    def open_spider(self, spider):
        key = os.environ.get("ANTHROPIC_API_KEY")

        if not key:
            spider.logger.warning("LLM désactivé (pas de clé API).")
            self.enabled = False
            return

        self.client = anthropic.Anthropic(api_key=key)
        self.enabled = True
        spider.logger.info("LLM activé.")

    def process_item(self, item, spider):
        if not getattr(self, "enabled", False):
            return item

        a = ItemAdapter(item)

        if a.get("win_pct") is None:
            return item

        try:
            resp = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=20,
                messages=[{
                    "role": "user",
                    "content": (
                        f"NHL team {a.get('name')} in {a.get('year')}. "
                        "Classify into: Original Six, Expansion Era, Modern Era. "
                        "Return ONLY one label."
                    )
                }]
            )

            era = resp.content[0].text.strip()

            if era in self.VALID_ERAS:
                a["era"] = era
            else:
                a["era"] = "Unknown"

        except Exception as e:
            spider.logger.warning(f"LLM error: {e}")
            a["era"] = "Unknown"

        return item


# ─────────────────────────────────────────────
# 3. SQLITE STORAGE
# ─────────────────────────────────────────────
class SQLitePipeline:

    def open_spider(self, spider):
        self.con = sqlite3.connect("hockey.db")

        self.con.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                name TEXT,
                year INTEGER,
                wins INTEGER,
                losses INTEGER,
                ot_losses INTEGER,
                win_pct REAL,
                goals_for INTEGER,
                goals_against INTEGER,
                era TEXT,
                PRIMARY KEY (name, year)
            )
        """)

        self.con.commit()

    def close_spider(self, spider):
        self.con.close()

    def process_item(self, item, spider):
        a = ItemAdapter(item)

        # 👉 Hockey only
        if a.get("name"):

            self.con.execute("""
                INSERT INTO teams (
                    name, year, wins, losses,
                    ot_losses, win_pct,
                    goals_for, goals_against, era
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name, year) DO UPDATE SET
                    wins=excluded.wins,
                    losses=excluded.losses,
                    win_pct=excluded.win_pct,
                    era=excluded.era
            """, (
                a.get("name"),
                a.get("year"),
                a.get("wins"),
                a.get("losses"),
                a.get("ot_losses"),
                a.get("win_pct"),
                a.get("goals_for"),
                a.get("goals_against"),
                a.get("era"),
            ))

            self.con.commit()

        return item