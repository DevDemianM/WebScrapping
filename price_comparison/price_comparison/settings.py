

BOT_NAME = "price_comparison"

SPIDER_MODULES = ["price_comparison.spiders"]
NEWSPIDER_MODULE = "price_comparison.spiders"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
