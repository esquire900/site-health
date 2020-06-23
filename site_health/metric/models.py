import requests
from django.db import models
from django.utils import timezone

from metric.utils import dt_str_to_sec_diff_now
from scraper.models import BaseScraper, SSLCertScraper, HeadersScraper, GetScraper
from website.models import Page


class MetricRequirements:
    required_scraper = BaseScraper
    once_per_domain = False
    max_age = 60


# Create your models here.
class Metric(models.Model):
    time = models.DateTimeField()
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    scraper_data = None

    class Requirements(MetricRequirements):
        pass

    class Meta:
        abstract = True
        # managed = False

    def generate(self):
        pass

    def get_data(self):
        return self.scraper_data

    def run(self):
        if self.Requirements.required_scraper is None:
            raise Exception("nothing to do here")
        scraper = self.Requirements.required_scraper

        ## see if there already exists a scrape that satisfies the requirement
        existing = (
            scraper.objects.filter(
                page=self.page,
                scraped_at__gt=timezone.now()
                - timezone.timedelta(seconds=self.Requirements.max_age),
            )
            .order_by("-scraped_at")
            .all()
        )
        if len(existing) == 0:
            scraper = scraper().factory(self.page)
        else:
            scraper = existing[0]
        self.scraper_data = scraper.get_data()

        self.time = scraper.scraped_at
        self.generate()
        self.save()

    def factory(self, page: Page):
        inst = self.__class__()
        inst.page = page
        return inst


class SSLExpiration(Metric):
    seconds_till_expiration = models.IntegerField()
    seconds_till_activation = models.IntegerField()

    class Requirements(MetricRequirements):
        once_per_domain = True
        required_scraper = SSLCertScraper
        max_age = 60 * 60

    def generate(self):
        import OpenSSL

        cert = self.get_data()
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)

        self.seconds_till_expiration = dt_str_to_sec_diff_now(x509.get_notAfter())
        self.seconds_till_activation = dt_str_to_sec_diff_now(x509.get_notBefore())


class HeaderMetrics(Metric):
    status_code = models.SmallIntegerField()
    content_length = models.IntegerField(null=True)
    sec_since_last_modified = models.IntegerField(null=True)

    class Requirements(MetricRequirements):
        once_per_domain = False
        required_scraper = HeadersScraper
        max_age = 10

    def generate(self):
        r = self.get_data()  # type: requests.models.Response
        self.status_code = r.status_code

        if "Content-Length" in r.headers.keys():
            self.content_length = r.headers["Content-Length"]
        if "Last-Modified" in r.headers.keys():
            self.sec_since_last_modified = dt_str_to_sec_diff_now(
                r.headers["Last-Modified"]
            )


class RedirectMetrics(Metric):
    num_redirects = models.SmallIntegerField()
    redirect_is_permanent = models.BooleanField(null=True)

    class Requirements(MetricRequirements):
        once_per_domain = False
        required_scraper = GetScraper
        max_age = 60 * 10

    def generate(self):
        r = self.get_data()  # type: requests.models.Response
        self.num_redirects = len(r.history)
        if len(r.history) > 0:
            self.redirect_is_permanent = r.history[0].is_permanent_redirect
