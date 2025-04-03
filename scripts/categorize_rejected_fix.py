import csv
import json
import os

from tqdm import tqdm

from utils.miscellaneous import extract_json_from_string



def categorize_rejcted_fixes():
    visited_id = set()
    with open('data_processed/rejected_reasons/rejected fix final.csv', 'r') as f:
        for line in csv.reader(f):
            visited_id.add(int(line[0]))

    with open('data_processed/rejected_reasons/reject_reasons.csv', 'r') as f:
        csv_reader = csv.reader(f)
        to_do = []
        for row in csv_reader:
            id = int(row[0])
            if id in visited_id:
                continue
            to_do.append(row)
        for row in tqdm(to_do, desc='Categorizing rejected fixes'):
            id = int(row[0])
            reason = row[2]
            title = row[1]
            if reason == 'no rejection':
                with open('data_processed/rejected_reasons/rejected fix final.csv', 'a') as fw:
                    writer = csv.writer(fw, quoting=csv.QUOTE_ALL)
                    writer.writerow([id, title, 'no rejection'])
                    continue

            summary = 'Title: ' + title + " Reason: " + reason
            categories = []



            with open('data_processed/rejected_reasons/rejected_reason_categories.csv', 'r') as f:
                for line in csv.reader(f):
                    categories.append(line[0].lower())
            print('title:', title)
            print('summary:', summary)
            print('categories:', categories)
