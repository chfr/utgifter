import csv
import io
import datetime


def parse_nordea(data):
    csvfile = io.StringIO(data)
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        amt = row["Belopp"]
        amt = float(amt.replace(".", "").replace(",", "."))

        poorly_formatted_date = row["Bokföringsdag"]
        parsed_date = datetime.datetime.strptime(poorly_formatted_date, "%Y/%m/%d")

        yield {"date": parsed_date.strftime("%Y-%m-%d"), "name": row["Rubrik"], "amount": amt}
