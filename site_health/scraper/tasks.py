import requests
from bs4 import BeautifulSoup
from celery import Task
from celery import shared_task
from django.core.cache import cache
from selenium.common.exceptions import WebDriverException

from scraper.models import GetScraper, SeleniumScraper
from website.models import Site, Page


@shared_task
def scrape_indexing_url(site_id, url=None):
    site = Site.objects.get(id=site_id)
    if url is None:
        page, was_created = Page.objects.get_or_create(url=site.url, site_id=site_id)
    else:
        page = Page.objects.get(url=url, site_id=site_id)
    cache_key = "scrape_indexing/{}".format(page.url)
    if cache.get(cache_key) is not None:
        raise Exception("Already started indexing this?")
    r = GetScraper().factory(page).get_data()  # type: requests.models.Response
    soup = BeautifulSoup(r.text, features="html.parser")
    links = []

    countdown = 5
    for link in soup.find_all("a", href=True):
        link = link["href"]
        if link[0] == "#":
            continue
        link = link.split("#")[0]
        if link[: len(str(site.url))] != str(site.url):
            continue
        if link not in links:
            links.append(link)
            page, was_created = Page.objects.get_or_create(site=site, url=link)
            cache_key = "scrape_indexing/{}".format(page.url)

            if was_created or cache.get(cache_key) is None:
                scrape_indexing_url.apply_async(
                    (site_id, page.url), countdown=countdown
                )
                countdown += 5
            cache.set(cache_key, 1, 10 * 60)


class SeleniumScraperTask(Task):
    _driver = None

    @property
    def driver(self):
        if self._driver is None:
            from selenium import webdriver
            self._driver = webdriver.Remote(
                desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
                command_executor='http://localhost:4444/wd/hub'
            )
            self._driver.desired_capabilities['zal:recordVideo'] = False
        return self._driver

    @property
    def empty_driver(self):
        self._driver = None
        return None


@shared_task(base=SeleniumScraperTask)
def selenium_scraper_execute(scrape_id):
    scraper = SeleniumScraper.objects.get(id=scrape_id)
    scraper.set_driver(selenium_scraper_execute.driver)
    try:
        scraper.get_data()
    except WebDriverException as e:
        if 'was terminated due to ORPHAN' in e.msg:
            # driver became stale, reinit
            _driver = None
            emptied = selenium_scraper_execute.empty_driver
            scraper.set_driver(selenium_scraper_execute.driver)
            scraper.get_data()
