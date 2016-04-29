import json
from datetime import date

from .models import Tag, SearchString, Matcher, Charge


def dump_data_to_json(user):
    data = []

    tags = Tag.objects.filter(user=user)

    for tag in tags:
        d = {"name": tag.name, "color": tag.color}

        matchers = Matcher.objects.filter(user=user, tag=tag)
        matcher_list = []
        for matcher in matchers:
            matcher_data = {"name": matcher.name, "method": matcher.method}

            searchstrings = SearchString.objects.filter(user=user, matcher=matcher)
            l = []
            for searchstring in searchstrings:
                l.append(searchstring.string)

            matcher_data["searchstrings"] = l
            matcher_list.append(matcher_data)

        d["matchers"] = matcher_list

        data.append(d)

    return json.dumps(data, indent=2)


def load_data_from_json(user, data):
    try:
        return load_data_from_json_unsafe(user, data)
    except Exception as e:
        print("Error loading data from json:")
        print(e)


def load_data_from_json_unsafe(user, data):
    user_charges = Charge.objects.filter(user=user)
    for jtag in data:
        tag, tcreated = Tag.objects.get_or_create(user=user, name=jtag["name"], color=jtag["color"])
        charges = user_charges.filter(tag=tag, matcher=None)

        for jmatcher in jtag["matchers"]:
            matcher, mcreated = Matcher.objects.get_or_create(user=user, name=jmatcher["name"],
                                                              method=jmatcher["method"], tag=tag)

            for jsearchstring in jmatcher["searchstrings"]:
                searchstring, screated = SearchString.objects.get_or_create(user=user, matcher=matcher,
                                                                            string=jsearchstring)

                for charge in charges:  # if any charge has this tag, apply the matcher that would've matched it
                    if matcher.match(searchstring.string, charge.name):
                        charge.matcher = matcher
                        charge.save()


def sanitize_date(year, month):
    return sanitize_year(year), sanitize_month(month)


# Takes a month number as a string or integer and returns it as an integer.
# Invalid month values return the current month number instead.
def sanitize_month(var):
    month = 0
    if month is None:
        month = 0

    if isinstance(var, str):
        try:
            month = int(var)
        except:
            month = 0
    elif isinstance(var, int):
        month = var

    if month < 0 or month > 12:
        month = 0

    if month == 0:
        month = current_month_number()

    return month


# Takes a year number as a string or integer and returns it as an integer.
# Invalid year values return the current year instead.
def sanitize_year(var):
    year = 0
    if year is None:
        year = 0

    if isinstance(var, str):
        try:
            year = int(var)
        except:
            year = 0
    elif isinstance(var, int):
        year = var

    if year < 0:  # jesus didn't have internet banking
        year = 0

    if year == 0:
        year = current_year_number()

    return year


def current_month_number():
    return date.today().month


def current_year_number():
    return date.today().year
