import scrapy
from hockey_scraper.items import HockeyTeamItem

BASE = "https://www.scrapethissite.com/pages/forms/"


class HockeySpider(scrapy.Spider):
    """
    Collecte les ~580 équipes-saisons NHL.

    Pagination : per_page=100 → 6 requêtes au lieu de 24.
    Arrêt     : page vide = fin de données (condition fiable).
    Formulaire: -a team="Boston" ou -a year="1998" pour filtrer.
    """

    name = "hockey"
    allowed_domains = ["www.scrapethissite.com"]

    def __init__(self, team=None, year=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_team = team
        self.filter_year = year

    def start_requests(self):
        params = {"page_num": "1", "per_page": "100"}
        if self.filter_team:
            params["q"] = self.filter_team
        if self.filter_year:
            params["q"] = self.filter_year
        yield scrapy.FormRequest(url=BASE, formdata=params,
                                 callback=self.parse,
                                 cb_kwargs={"params": params, "page": 1},
                                 dont_filter=True)

    def parse(self, response, params, page):
        rows = response.css("tr.team")

        if not rows:
            self.logger.info(f"Page {page} vide — pagination terminée.")
            return

        self.logger.info(f"Page {page} → {len(rows)} équipes")

        for row in rows:
            def cell(cls, r=row):
                return r.css(f".{cls}::text").get("").strip()

            item = HockeyTeamItem()
            item["name"]          = cell("name")
            item["year"]          = cell("year")
            item["wins"]          = cell("wins")
            item["losses"]        = cell("losses")
            item["ot_losses"]     = cell("ot-losses") or None
            item["win_pct"]       = cell("pct")
            item["goals_for"]     = cell("gf")
            item["goals_against"] = cell("ga")
            item["era"]           = None
            yield item

        next_params = {**params, "page_num": str(page + 1)}
        yield scrapy.FormRequest(url=BASE, formdata=next_params,
                                 callback=self.parse,
                                 cb_kwargs={"params": next_params, "page": page + 1},
                                 dont_filter=True)
