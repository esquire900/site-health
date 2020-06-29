from django.apps import AppConfig


class MetricConfig(AppConfig):
    name = "site_health.metric"

    def ready(self):
        import site_health.metric.signals  # noqa
