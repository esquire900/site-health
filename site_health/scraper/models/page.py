import requests

from site_health.scraper.models import BaseScraper, ScraperPickleCache


class RequestsSettings:
    connection_timeout = 5
    read_timeout = 20
    headers = {
        "User-Agent": "Mozilla/5.0+(compatible; SiteHealth/1.0;)",
        "Cache-Control": "max-age=0",
        "Accept-Language": "en-US,en;q=0.5",
    }


class PageScraper(BaseScraper, ScraperPickleCache):
    """
    Saves a python requests get as pickle
    """

    def _scrape(self):
        return requests.get(
            self.page.full_url,
            timeout=(
                RequestsSettings.connection_timeout,
                RequestsSettings.read_timeout,
            ),
            headers=RequestsSettings.headers,
        )
