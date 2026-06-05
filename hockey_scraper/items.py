import scrapy


class HockeyTeamItem(scrapy.Item):
    """Un enregistrement = une équipe sur une saison."""
    name          = scrapy.Field()  # str
    year          = scrapy.Field()  # int
    wins          = scrapy.Field()  # int
    losses        = scrapy.Field()  # int
    ot_losses     = scrapy.Field()  # int | None (absent avant ~2000)
    win_pct       = scrapy.Field()  # float
    goals_for     = scrapy.Field()  # int
    goals_against = scrapy.Field()  # int
    era           = scrapy.Field()  # str — enrichi par LLM (bonus)


class OscarFilmItem(scrapy.Item):
    """Bonus AJAX — film oscarisé."""
    title        = scrapy.Field()  # str
    year         = scrapy.Field()  # int
    awards       = scrapy.Field()  # int
    nominations  = scrapy.Field()  # int
    best_picture = scrapy.Field()  # bool
