from django import forms
from scraper.tasks import scrape_indexing_url
from website.models import Site


class WebsiteStartIndexingForm(forms.Form):
    site_id = forms.IntegerField()

    def start_indexing(self):
        site = Site.objects.get(id=self.cleaned_data["site_id"])
        scrape_indexing_url.delay(site.id)
