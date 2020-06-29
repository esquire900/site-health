import os
import pickle
import uuid

import django.dispatch
from django.db import models
from django.utils import timezone

from config.settings.base import SCRAPER_CACHE
from site_health.scraper.processor import HtmlProcessor
from site_health.website.models import Page


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


scrape_complete = django.dispatch.Signal(providing_args=["scraper"])


class BaseScraper(models.Model, ScraperPickleCache):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    planned_at = models.DateTimeField(default=timezone.now, db_index=True)
    scraped_at = models.DateTimeField(null=True, db_index=True)
    status = models.SmallIntegerField(default=0, db_index=True)

    _status_choices = {
        0: "init",
        1: "in_queue",
        5: "scraped",
        9: "cache_removed",
        11: "scraping_not_allowed",
    }

    def get_status(self):
        return self._status_choices[self.status]

    @property
    def cache_fname(self, file_extension=None):
        if file_extension is None:
            file_extension = self.file_extension

        fname = SCRAPER_CACHE + "{}/{}/{}/".format(
            self.page.site_id, self.page_id, self.__class__.__name__
        )
        if not os.path.exists(fname):
            os.makedirs(fname)
        fname += str(self.id) + ".{}".format(file_extension)
        return fname

    def factory(self, page: Page, planned_at=timezone.now()):
        scraper = self.__class__(id=uuid.uuid4(), page=page, planned_at=planned_at)
        scraper.save()
        return scraper

    def is_data_available(self):
        return self.status == 5

    def run(self):
        """

        :return: False | requests.models.Response
        """

        if self.status >= 9:
            return False  # not available anymore

        if self.status == 5:
            return self.get_cache(self.cache_fname)

        if not self.page.is_scraping_allowed:
            self.status = 11
            self.save()
            return False

        if self.status <= 1:
            res = self._scrape()
            self.status = 5
            self.scraped_at = timezone.now()
            self.save()
            self.set_cache(self.cache_fname, res)
            scrape_complete.send_robust(sender=self.__class__, scraper=self)
            return res

    def get_html_processor(self):
        return HtmlProcessor(self.run().text, self.page)

    def _scrape(self):
        raise NotImplementedError()
