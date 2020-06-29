# import os
# import pickle
# import time
# import uuid
#
# import pandas as pd
# import requests
# from django.core.validators import MaxValueValidator, MinValueValidator
# from django.db import models
# from selenium import webdriver
#
# from config.settings.base import SCRAPER_CACHE
# from site_health.website.models import Page, Site
# from site_health.scraper.processor import HtmlProcessor
# from site_health.users.models import User
#
#
# class SSLScheduler(models.Model):
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)
#     run_every = models.IntegerField(default=60 * 60 * 24)
#     next_scheduled = models.DateTimeField()
#
#
# class ScraperConfig(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     page = models.ForeignKey(Page, null=True, on_delete=models.CASCADE, default=None)
#     site = models.ForeignKey(Site, null=True, on_delete=models.CASCADE, default=None)
#     scraper_type = models.SmallIntegerField()
#     run_every = models.IntegerField(default=60 * 60 * 24)
#     next_scheduled = models.DateTimeField()
#
#     class Meta:
#         unique_together = ("user", "page", "site", "scraper_type")
#
#     def save(
#         self, force_insert=False, force_update=False, using=None, update_fields=None
#     ):
#         assert self.scraper_type in ["get", "header", "selenium", "ssl"]
#
#     @staticmethod
#     def resolve_for_page(page: Page):
#         """
#         Returns the delay in seconds for the next scrape, given a page and scraper type
#         :param page: page for which to resolve the config
#         :param scraper_type: str, one of ["get", "header", "selenium", "ssl"]
#         :return: int | False
#         """
#         user = page.site.owner
#         page_config = ScraperConfig.objects.filter(page=page).first()
#         site_config = ScraperConfig.objects.filter(site=page.site).first()
#         base_config = ScraperConfig.objects.get(
#             user=user, page__isnull=True, site__isnull=True
#         )
#
#         config = base_config.__dict__
#         if site_config:
#             config.update(site_config.__dict__)
#         if page_config:
#             config.update(page_config.__dict__)
#         if scraper_type is "ssl":
#             return config["scraper_ssl_speed"]
#
#         if page.is_home:
#             if scraper_type is "get":
#                 return config["scraper_get_home_speed"]
#             elif scraper_type is "selenium":
#                 return config["scraper_selenium_home_speed"]
#         else:
#             if scraper_type is "get":
#                 return config["scraper_get_pages_speed"]
#             elif scraper_type is "selenium":
#                 return config["scraper_selenium_pages_speed"]
#         return False
