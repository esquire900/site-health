import os
import pickle
import time
import uuid

import pandas as pd
import requests
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from selenium import webdriver

from config.settings.base import STATIC_CACHE
from website.models import Page


class ScraperCache:
    file_extension = "cache"

    @staticmethod
    def get_cache(self):
        pass

    @staticmethod
    def set_cache(self, res):
        pass


class ScraperPickleCache(ScraperCache):
    file_extension = "pkl"

    @staticmethod
    def get_cache(file_name):
        if os.path.exists(file_name):
            return pickle.load(open(file_name, "rb"))
        return False

    @staticmethod
    def set_cache(file_name, res):
        with open(file_name, "wb") as f:
            pickle.dump(res, f)


class ScraperFileCache(ScraperCache):
    file_extension = "file"

    @staticmethod
    def get_cache(file_name):
        if os.path.exists(file_name):
            return open(file_name).read()
        return False

    @staticmethod
    def set_cache(file_name, res):
        with open(file_name, "w") as f:
            f.write(res)


class BaseScraper(models.Model, ScraperPickleCache):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    scraped_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=0)

    _status_choices = {0: "init", 1: "scraped", 9: "cache_removed"}

    def get_status(self):
        return self._status_choices[self.status]

    @property
    def cache_fname(self, file_extension=None):
        if file_extension is None:
            file_extension = self.file_extension

        fname = STATIC_CACHE + "/cache/{}/{}/{}/".format(
            self.page.site_id, self.page_id, self.__class__.__name__
        )
        if not os.path.exists(fname):
            os.makedirs(fname)
        fname += str(self.id) + ".{}".format(file_extension)
        return fname

    def factory(self, page: Page):
        scraper = self.__class__(id=uuid.uuid4(), page=page,)
        scraper.save()
        return scraper

    def get_data(self):
        if self.status == 9:
            return False  # not available anymore
        if self.status == 0:
            res = self._scrape()
            self.status = 1
            self.save()
            self.set_cache(self.cache_fname, res)
            return res
        if self.status == 1:
            return self.get_cache(self.cache_fname)

    def _scrape(self):
        raise NotImplementedError()


class RequestsSettings:
    connection_timeout = 5
    read_timeout = 20


class GetScraper(BaseScraper, ScraperPickleCache):
    """
    Saves a python requests get as pickle
    """

    def _scrape(self):
        return requests.get(
            self.page.url,
            timeout=(
                RequestsSettings.connection_timeout,
                RequestsSettings.read_timeout,
            ),
        )


class HeadersScraper(BaseScraper, ScraperPickleCache):
    """
    Saves a python requests header as pickle
    """

    def _scrape(self):
        return requests.head(
            self.page.url,
            timeout=(
                RequestsSettings.connection_timeout,
                RequestsSettings.read_timeout,
            ),
        )


class SSLCertScraper(BaseScraper, ScraperFileCache):
    """
    Saves a ssl certificate as string
    """

    def _scrape(self):
        import ssl

        # todo timeouts
        url = self.page.url.replace("http://", "").replace("https://", "").split("/")[0]
        cert = ssl.get_server_certificate((url, 443))
        return cert


class SeleniumScraper(BaseScraper, ScraperPickleCache):
    driver = None  # type: webdriver.Remote
    take_screenshot = models.BooleanField(default=False)
    screen_width = models.IntegerField(
        default=1280, validators=[MaxValueValidator(1800), MinValueValidator(200)]
    )
    wait_ms_before_screenshot = models.IntegerField(
        default=300, validators=[MaxValueValidator(1000), MinValueValidator(0)]
    )

    def set_driver(self, driver: webdriver.Remote):
        self.driver = driver

    @property
    def screenshot_file(self):
        if self.take_screenshot is False:
            return False
        if self.status != 1:
            return False
        return self.cache_fname("png")

    def _scrape(self):
        if self.driver is None:
            raise Exception("No driver set")

        self.driver.get(self.page.url)

        timings = self.driver.execute_script("return performance.timing")

        # all entries
        df = pd.DataFrame(self.driver.execute_script("return performance.getEntries()"))
        html = self.driver.find_element_by_xpath("//body").get_attribute("outerHTML")

        if self.take_screenshot:
            # modify screen size to exactly fit full page, take screenshot
            get_prop = lambda x: self.driver.execute_script(
                "return document.body.parentNode.scroll" + x
            )
            self.driver.set_window_size(self.screen_width, get_prop("Height"))
            sleepy_time = self.wait_ms_before_screenshot / 1000
            sleepy_time = min(1.0, sleepy_time)  # just to make sure
            time.sleep(sleepy_time)
            cache_name = self.cache_fname.replace(".pkl", ".png")
            self.driver.find_element_by_tag_name("body").screenshot(cache_name)

        result = {"df": df, "html": html, "timings": timings}
        return result
