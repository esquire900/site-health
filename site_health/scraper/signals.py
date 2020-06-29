from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from site_health.scraper.models import SSLCertScraper
from site_health.scraper.models import scrape_complete, PageScraper, PageBrowserScraper
from site_health.website.models import Page


@receiver(scrape_complete, sender=PageScraper)
def scrape_page_request_for_urls(sender, scraper: PageScraper, **kwargs):
    processor = scraper.get_html_processor()
    for url in processor.extract_urls_to_self():
        Page.objects.get_or_create(site=scraper.page.site, url_part=url)


SSL_EVERY = 24 * 60 * 60
PAGE_EVERY = 60 * 60
PAGE_BROWSER_EVERY = 60 * 60 * 24
PAGE_HOME_EVERY = 60 * 10
PAGE_BROWSER_HOME_EVERY = 60 * 10


@receiver(post_save, sender=Page)
def setup_init_page_scrapers(sender, instance: Page, created, **kwargs):

    if not created:
        return None

    if instance.is_home:

        scrape_planner(SSLCertScraper, instance, tdiff_seconds=0)
        scrape_planner(PageScraper, instance, tdiff_seconds=0)
        scrape_planner(PageBrowserScraper, instance, tdiff_seconds=0)
    else:
        scrape_planner(PageScraper, instance, tdiff_seconds=PAGE_EVERY)
        scrape_planner(PageBrowserScraper, instance, tdiff_seconds=PAGE_BROWSER_EVERY)


@receiver(scrape_complete, sender=SSLCertScraper)
def setup_next_ssl_scraper(sender, scraper: SSLCertScraper, **kwargs):
    scrape_planner(SSLCertScraper, scraper.page, tdiff_seconds=SSL_EVERY)


@receiver(scrape_complete, sender=PageScraper)
def setup_next_page_scraper(sender, scraper: PageScraper, **kwargs):
    if scraper.page.is_home:
        scrape_planner(PageScraper, scraper.page, tdiff_seconds=PAGE_EVERY)
    else:
        scrape_planner(PageScraper, scraper.page, tdiff_seconds=PAGE_HOME_EVERY)


@receiver(scrape_complete, sender=PageBrowserScraper)
def setup_next_page_browser_scraper(sender, scraper: PageBrowserScraper, **kwargs):
    if scraper.page.is_home:
        scrape_planner(PageScraper, scraper.page, tdiff_seconds=PAGE_BROWSER_HOME_EVERY)
    else:
        scrape_planner(PageScraper, scraper.page, tdiff_seconds=PAGE_BROWSER_EVERY)


def scrape_planner(scrape_class, page: Page, tdiff_seconds):
    assert scrape_class in [SSLCertScraper, PageScraper, PageBrowserScraper]
    n_planned = scrape_class.objects.filter(page=page, status=0).count()

    if n_planned > 0:
        return True  # we can only plan one
    planned = timezone.now() + timezone.timedelta(seconds=tdiff_seconds)

    # last = (
    #     scrape_class.objects.filter(page__site=page.site, planned_at__gt=planned)
    #     .order_by("planned_at")
    #     .last()
    # )

    if tdiff_seconds > 0:
        import numpy as np

        # plan with some variance
        rnd = np.random.randint(
            np.round(tdiff_seconds * 0.7), np.round(tdiff_seconds * 1.3)
        )
        planned = timezone.now() + timezone.timedelta(seconds=rnd)
    scrape_class().factory(
        page=page, planned_at=planned,
    )
