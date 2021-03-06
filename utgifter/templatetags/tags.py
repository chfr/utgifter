from datetime import date

from django import template

register = template.Library()


@register.filter
def month_name(month):
    d = date(2016, month, 1)
    return d.strftime("%B")


@register.filter
def month_name_short(month):
    return month_name(month)[:3]
