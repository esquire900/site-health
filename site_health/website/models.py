# Create your models here.
import tld
from django.db import models
from django.urls import reverse

from site_health.users.models import User
from django_lifecycle import LifecycleModelMixin, hook, AFTER_CREATE, BEFORE_CREATE


class Site(LifecycleModelMixin, models.Model):
    url = models.URLField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        return reverse("websites:detail", args=[self.id])

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
            Page.factory(self, "")


class Page(LifecycleModelMixin, models.Model):
    url_part = models.CharField(max_length=1024)
    site = models.ForeignKey("Site", on_delete=models.CASCADE)
    is_home = models.BooleanField(default=False)

    def __str__(self):
        return self.full_url

    @property
    def full_url(self):
        return self.site.url + self.url_part

    @staticmethod
    def factory(site: Site, url_part):
        # strip url_part
        return Page.objects.create(url_part=url_part, site=site)

    @hook(BEFORE_CREATE)
    def before_create(self):
        self.url_part = self.url_part.replace(self.site.url, "")
