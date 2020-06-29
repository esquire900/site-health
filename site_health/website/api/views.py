from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from .serializers import PageSerializer, SiteSerializer
from site_health.website.models import Site, Page


class SiteViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = SiteSerializer
    queryset = Site.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner_id=self.request.user.id)


class PageViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = PageSerializer
    queryset = Page.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(site__owner_id=self.request.user.id)
