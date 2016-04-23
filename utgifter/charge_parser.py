import csv
import io


def parse_nordea(data):
    csvfile = io.StringIO(data)
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        amt = row["Belopp"]
        amt = float(amt.replace(".", "").replace(",", "."))

        yield {"date": row["Datum"], "name": row["Transaktion"], "amount": amt}
