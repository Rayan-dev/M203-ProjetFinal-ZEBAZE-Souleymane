import scrapy
from hockey_scraper.items import HockeyTeamItem


class HockeySpider(scrapy.Spider):
    name = "hockey"
    allowed_domains = ["www.scrapethissite.com"]
    start_urls = ["https://www.scrapethissite.com/pages/forms/"]
    
    custom_settings = {
        "FEEDS": {
            "hockey_teams.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }
    
    def parse(self, response):
        rows = response.css("table tr.team")
        
        for row in rows:
            item = HockeyTeamItem()
            item["name"] = row.css("td.name::text").get().strip()
            item["year"] = row.css("td.year::text").get().strip()
            item["wins"] = row.css("td.wins::text").get().strip()
            item["losses"] = row.css("td.losses::text").get().strip()
            
            ot_losses = row.css("td.ot-losses::text").get()
            item["ot_losses"] = ot_losses.strip() if ot_losses else None
            
            item["win_pct"] = row.css("td.pct::text").get().strip()
            item["goals_for"] = row.css("td.gf::text").get().strip()
            item["goals_against"] = row.css("td.ga::text").get().strip()
            item["era"] = None
            
            yield item
        
        # Pagination
        pages = response.css("ul.pagination li a::attr(href)").getall()
        current_page_num = response.url.split("page_num=")[-1] if "page_num=" in response.url else "1"
        
        try:
            current_idx = pages.index(f"/pages/forms/?page_num={current_page_num}")
            if current_idx + 1 < len(pages):
                next_page = pages[current_idx + 1]
                yield response.follow(next_page, callback=self.parse)
        except (ValueError, IndexError):
            pass