import csv
from typing import List, Dict, Any

def export_to_csv(data: List[Dict[str, Any]], filename: str):
    if not data:
        return
    
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
