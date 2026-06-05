import scrapy
from hockey_scraper.items import OscarFilmItem

AJAX_URL = "https://www.scrapethissite.com/pages/ajax-javascript/"


class OscarsSpider(scrapy.Spider):
    """
    Bonus — Réflexe API cachée (barreau 1).

    Recon DevTools : Network > Fetch/XHR révèle ?ajax=true&year=YYYY → JSON pur.
    On appelle l'endpoint directement, sans HTML ni Playwright.
    Années disponibles : 2010–2015.
    """

    name = "oscars"
    allowed_domains = ["www.scrapethissite.com"]
    start_urls = [AJAX_URL]
    
    custom_settings = {
        "FEEDS": {
            "oscars.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def parse(self, response):
        # Ignorer cette réponse et générer les vraies requêtes
        for year in range(2010, 2016):
            url = f"{AJAX_URL}?ajax=true&year={year}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_json,
                cb_kwargs={"year": year},
                dont_filter=True,
            )

    def parse_json(self, response, year):
        try:
            films = response.json()
        except Exception as e:
            self.logger.error(f"JSON invalide {year}: {e}")
            return

        self.logger.info(f"Oscars {year} → {len(films)} films")
        for film in films:
            item = OscarFilmItem()
            item["title"]        = film.get("title", "").strip()
            item["year"]         = year
            item["awards"]       = film.get("awards", 0)
            item["nominations"]  = film.get("nominations", 0)
            item["best_picture"] = film.get("best_picture", False)
            yield item
