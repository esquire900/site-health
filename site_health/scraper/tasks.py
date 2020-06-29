from abc import ABC

from celery import Task
from celery import shared_task
from django.utils import timezone
from selenium.common.exceptions import WebDriverException

from site_health.scraper.models import PageBrowserScraper
from site_health.scraper.models import PageScraper, SSLCertScraper


class SeleniumScraperTask(Task, ABC):
    _driver = None

    @property
    def driver(self):
        if self._driver is None:
            from selenium import webdriver

            self._driver = webdriver.Remote(
                desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
                command_executor="http://localhost:4444/wd/hub",
            )
        return self._driver

    @property
    def empty_driver(self):
        self._driver = None
        return None


@shared_task(base=SeleniumScraperTask)
def selenium_scraper_execute(scrape_id):
    scraper = PageBrowserScraper.objects.get(id=scrape_id)
    scraper.set_driver(selenium_scraper_execute.driver)
    try:
        scraper.run()
    except WebDriverException as e:
        if "was terminated due to ORPHAN" in e.msg:
            # driver became stale, reinit
            _driver = None
            emptied = selenium_scraper_execute.empty_driver
            scraper.set_driver(selenium_scraper_execute.driver)
            scraper.run()


@shared_task
def run_scraper(kind, scraper_id):
    scraper = None
    if kind == "ssl":
        scraper = SSLCertScraper.objects.get(id=scraper_id)
    elif kind == "page":
        scraper = PageScraper.objects.get(id=scraper_id)
    elif kind == "page_browser":
        scraper = PageBrowserScraper.objects.get(id=scraper_id)
    if scraper is None:
        return False
    scraper.run()
    return True


@shared_task
def push_planned():
    for cls, cls_type in [(SSLCertScraper, "ssl"), (PageScraper, "page")]:
        scrapers = cls.objects.filter(
            status=0, planned_at__lte=timezone.now() + timezone.timedelta(seconds=10)
        ).all()
        for scraper in scrapers:
            if scraper.planned_at <= timezone.now():
                run_scraper.apply_async((cls_type, scraper.id))
            else:
                run_scraper.apply_async((cls_type, scraper.id), eta=scraper.planned_at)
