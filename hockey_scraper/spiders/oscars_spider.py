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

    def start_requests(self):
        for year in range(2010, 2016):
            yield scrapy.Request(
                url=f"{AJAX_URL}?ajax=true&year={year}",
                callback=self.parse_json,
                cb_kwargs={"year": year},
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
