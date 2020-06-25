from django.urls import path

from site_health.website.views import (
    site_detail_view,
    site_list_view,
    start_indexing_website,
    create_site,
)

app_name = "websites"
urlpatterns = [
    path("<int:pk>/view", view=site_detail_view, name="detail"),
    path("<int:pk>/start_indexing", view=start_indexing_website, name="start_indexing"),
    path("create", view=create_site, name="create"),
    path("", view=site_list_view, name="list"),
]
