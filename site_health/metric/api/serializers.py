from rest_framework import serializers

from site_health.metric.models import SSLExpiration


class SSLMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSLExpiration
        fields = ["page_id"]

        # extra_kwargs = {
        #     "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        # }
