from datetime import date


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
