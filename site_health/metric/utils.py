from dateutil import parser
from django.utils import timezone


def date_string_to_total_seconds(x):
    x = parser.parse(x)
    return int(round((x - timezone.now()).total_seconds()))
