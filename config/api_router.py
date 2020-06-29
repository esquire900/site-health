from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from site_health.users.api.views import UserViewSet
from site_health.metric.api.views import SSLMetricViewSet
from site_health.website.api.views import SiteViewSet, PageViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("ssl_metrics", SSLMetricViewSet, basename="ssl_metric")
router.register("sites", SiteViewSet, basename="site")
router.register("pages", PageViewSet, basename="page")

app_name = "api"
urlpatterns = router.urls
