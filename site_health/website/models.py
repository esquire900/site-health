# Create your models here.
import tld
from django.db import models
from django.urls import reverse
from django_lifecycle import LifecycleModelMixin, hook, AFTER_CREATE, BEFORE_CREATE

from site_health.users.models import User


class Site(LifecycleModelMixin, models.Model):
    url = models.URLField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_redirect_domain = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        return reverse("websites:detail", args=[self.id])

    @property
    def is_scraping_allowed(self):
        return self.is_active

    @property
    def domain(self):
        res = tld.get_tld(self.url, as_object=True, fail_silently=True)
        if res is None:
            return False
        domain = ""
        if res.subdomain:
            domain = res.subdomain + "."
        domain += res.fld
        return domain

    @hook(AFTER_CREATE)
    def after_create(self):
        if self.page_set.count() is 0:
            page = Page.objects.create(site=self, is_home=True, url_part="")
            page.save()


class Page(LifecycleModelMixin, models.Model):
    url_part = models.CharField(max_length=1024)
    site = models.ForeignKey("Site", on_delete=models.CASCADE)
    is_home = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_url

    class Meta:
        unique_together = ("url_part", "site")

    @property
    def is_scraping_allowed(self):
        return self.is_active and self.site.is_scraping_allowed

    @property
    def full_url(self):
        return self.site.url + self.url_part

    @hook(BEFORE_CREATE)
    def before_create(self):
        self.url_part = self.url_part.replace(self.site.url, "")
