# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, FormView, CreateView

from site_health.website.models import Site

from site_health.website.forms import WebsiteStartIndexingForm
from django.core.exceptions import ValidationError


class SiteDetailView(LoginRequiredMixin, DetailView):
    model = Site
    context_object_name = "site"


site_detail_view = SiteDetailView.as_view()


class SiteListView(LoginRequiredMixin, ListView):
    model = Site
    context_object_name = "sites"


site_list_view = SiteListView.as_view()

# Relative import of GeeksForm


class StartIndexingFormView(LoginRequiredMixin, FormView):
    form_class = WebsiteStartIndexingForm

    def get_success_url(self):
        referer_url = self.request.META.get("HTTP_REFERER")
        if referer_url:
            return referer_url
        return "/"

    def form_valid(self, form):
        site = Site.objects.get(id=form.cleaned_data["site_id"])
        if self.request.user.id is not site.owner_id:
            raise ValidationError
        form.start_indexing()
        return super().form_valid(form)


start_indexing_website = StartIndexingFormView.as_view()


class CreateSiteView(LoginRequiredMixin, CreateView):
    model = Site
    fields = [
        "url",
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)


create_site = CreateSiteView.as_view()
