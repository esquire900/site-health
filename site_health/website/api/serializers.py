from rest_framework import serializers

from site_health.website.models import Site, Page


class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = [
            "id",
            "full_url",
        ]


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Site
        fields = ["id", "pages"]
