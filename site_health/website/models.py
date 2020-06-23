# Create your models here.
import tld
from django.db import models

from site_health.users.models import User


class Site(models.Model):
    url = models.URLField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.url

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


class Page(models.Model):
    url_part = models.CharField(max_length=1024)
    site = models.ForeignKey('Site', on_delete=models.CASCADE)

    def __str__(self):
        return self.url

    @property
    def url(self):
        return self.site.url + self.url_part

    @staticmethod
    def factory(site: Site, url_part):
        return Page.objects.create(url_part=url_part, site=site)
