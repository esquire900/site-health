from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from .serializers import SSLMetricSerializer
from site_health.metric.models import SSLExpiration


class SSLMetricViewSet(
    RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet
):
    serializer_class = SSLMetricSerializer
    queryset = SSLExpiration.objects.all()
    lookup_field = "page"

    def get_queryset(self, *args, **kwargs):
        return self.queryset  # .filter(id=self.request.user.id)
