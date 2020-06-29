import requests
from django.db import models

from site_health.metric.utils import date_string_to_total_seconds
from site_health.scraper.models import BaseScraper
from site_health.scraper.models import PageScraper
from site_health.scraper.models import SSLCertScraper
from site_health.website.models import Page


class MetricRequirements:
    required_scraper = BaseScraper
    once_per_domain = False
    max_age = 60


# Create your models here.
class Metric(models.Model):
    time = models.DateTimeField()
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    scraper = None

    class Requirements(MetricRequirements):
        pass

    class Meta:
        abstract = True
        # managed = False

    def generate(self):
        pass

    def run(self, page: Page, scraper: BaseScraper):
        self.scraper = scraper
        self.page = page
        self.time = scraper.scraped_at
        self.generate()
        self.save()


class SSLExpiration(Metric):
    seconds_till_expiration = models.IntegerField()
    seconds_till_activation = models.IntegerField()

    class Requirements(MetricRequirements):
        required_scraper = SSLCertScraper

    def generate(self):
        import OpenSSL

        cert = self.scraper.run()
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)

        self.seconds_till_expiration = date_string_to_total_seconds(x509.get_notAfter())
        self.seconds_till_activation = date_string_to_total_seconds(
            x509.get_notBefore()
        )


class PageRequestMetrics(Metric):
    status_code = models.SmallIntegerField()
    content_length = models.IntegerField(null=True)
    sec_since_last_modified = models.IntegerField(null=True)
    elapsed_seconds = models.FloatField()
    num_redirects = models.SmallIntegerField()
    redirect_is_permanent = models.BooleanField(null=True)

    class Requirements(MetricRequirements):
        required_scraper = PageScraper

    def generate(self):
        r = self.scraper.run()  # type: requests.models.Response
        self.status_code = r.status_code
        self.elapsed_seconds = r.elapsed.total_seconds()
        self.content_length = len(r.content)
        if "Last-Modified" in r.headers.keys():
            self.sec_since_last_modified = -date_string_to_total_seconds(
                r.headers["Last-Modified"]
            )
        self.num_redirects = len(r.history)
        if len(r.history) > 0:
            self.redirect_is_permanent = r.history[0].is_permanent_redirect
