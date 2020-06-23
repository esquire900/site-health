from dateutil import parser
from django.utils import timezone


def dt_str_to_sec_diff_now(x):
    x = parser.parse(x)
    return int(round((x - timezone.now()).total_seconds()))
