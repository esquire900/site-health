import time

import pandas as pd
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from selenium import webdriver

from site_health.scraper.models import BaseScraper, ScraperPickleCache


class PageBrowserScraper(BaseScraper, ScraperPickleCache):
    driver = None  # type: webdriver.Remote
    take_screenshot = models.BooleanField(default=False)
    screen_width = models.IntegerField(
        default=1280, validators=[MaxValueValidator(1800), MinValueValidator(200)]
    )
    wait_ms_before_screenshot = models.IntegerField(
        default=300, validators=[MaxValueValidator(4000), MinValueValidator(0)]
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

        self.driver.get(self.page.full_url)

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
            sleepy_time = min(4.0, sleepy_time)  # just to make sure
            time.sleep(sleepy_time)
            cache_name = self.cache_fname.replace(".pkl", ".png")
            self.driver.find_element_by_tag_name("body").screenshot(cache_name)

        result = {"df": df, "html": html, "timings": timings}
        return result
