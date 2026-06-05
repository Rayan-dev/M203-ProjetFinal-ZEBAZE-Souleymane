BOT_NAME = "hockey_scraper"
SPIDER_MODULES  = ["hockey_scraper.spiders"]
NEWSPIDER_MODULE = "hockey_scraper.spiders"

# ── Identité ────────────────────────────────────────────────
USER_AGENT = "M203-IPSSI-ProjetFinal/1.0 (bac-a-sable; formation IPSSI)"

# ── Politesse ───────────────────────────────────────────────
DOWNLOAD_DELAY                  = 1.0
RANDOMIZE_DOWNLOAD_DELAY        = True
CONCURRENT_REQUESTS             = 4
CONCURRENT_REQUESTS_PER_DOMAIN  = 2

AUTOTHROTTLE_ENABLED            = True
AUTOTHROTTLE_START_DELAY        = 1.0
AUTOTHROTTLE_MAX_DELAY          = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# ── Résilience ──────────────────────────────────────────────
RETRY_ENABLED    = True
RETRY_TIMES      = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]
DOWNLOAD_TIMEOUT = 20

# ── Pipelines ───────────────────────────────────────────────
ITEM_PIPELINES = {
    "hockey_scraper.pipelines.NormalisePipeline": 100,
    "hockey_scraper.pipelines.LLMEnrichPipeline": 150,
    "hockey_scraper.pipelines.SQLitePipeline":    200,
}

# ── Exports JSON ────────────────────────────────────────────
FEEDS = {
    "hockey_teams.json": {
        "format": "json",
        "encoding": "utf8",
        "overwrite": True,
    },
    "oscars.json": {
        "format": "json",
        "encoding": "utf8",
        "overwrite": True,
    }
}

FEED_EXPORTERS = {
    "json": "scrapy.exporters.JsonItemExporter",
}

FEED_EXPORT_INDENT = 2

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
ROBOTSTXT_OBEY = False
