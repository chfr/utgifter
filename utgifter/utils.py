from datetime import date


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


def current_month_number():
    return date.today().month
