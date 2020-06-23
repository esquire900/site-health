from celery import shared_task


@shared_task
def run_metric(metric):
    return metric.run()
