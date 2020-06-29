from django.dispatch import receiver
from site_health.scraper.models import SSLCertScraper, scrape_complete, PageScraper
from site_health.metric.models import SSLExpiration, PageRequestMetrics


@receiver(scrape_complete, sender=SSLCertScraper)
def ssl_scraper_ran(sender, scraper, **kwargs):
    SSLExpiration().run(scraper.page, scraper)


@receiver(scrape_complete, sender=PageScraper)
def page_scraper_ran(sender, scraper, **kwargs):
    PageRequestMetrics().run(scraper.page, scraper)
