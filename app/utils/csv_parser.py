import csv
from io import TextIOWrapper


def parse_csv(file):
    reader = csv.DictReader(TextIOWrapper(file.file, encoding="utf-8"))
    return list(reader)