from site_health.scraper.models import BaseScraper, ScraperFileCache


class SSLCertScraper(BaseScraper, ScraperFileCache):
    """
    Saves a ssl certificate as string
    """

    def _scrape(self):
        import ssl

        # todo timeouts
        url = (
            self.page.full_url.replace("http://", "")
            .replace("https://", "")
            .split("/")[0]
        )
        cert = ssl.get_server_certificate((url, 443))
        return cert
