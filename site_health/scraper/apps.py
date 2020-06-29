from django.apps import AppConfig


class ScraperConfig(AppConfig):
    name = "site_health.scraper"

    def ready(self):
        import site_health.scraper.signals  # noqa
