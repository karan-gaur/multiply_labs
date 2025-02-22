import csv
from typing import List, Tuple

def read_process_from_csv(filepath: str) -> List[Tuple[str, str, int]]:
    operations = []
    with open(filepath, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            module, operation, duration = row
            operations.append((module, operation, int(duration)))
    return operations
