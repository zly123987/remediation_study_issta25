import csv
import os


def count_accepeted_rejected(c):
    target_ids = set()
    with open('data_collection/summaries/summaries_3col.csv', 'r', newline='', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            target_ids.add(row[0])
    with open('data_collection/cve/summaries_3col.csv', 'r', newline='', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            target_ids.add(row[0])

    with open('data_collection/target_issue_ids.csv', 'r') as f:
        for line in csv.reader(f):
            target_ids.add(line[0])
    os.makedirs('data_processed', exist_ok=True)
    with open('data_processed/acceptance.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['id', 'accept'])
    coll = c['remediation']['github_issues_non_bots']

    for doc in coll.find({'accept': {'$exists': True}}):
        with open('data_processed/acceptance.csv', 'a') as f:
            csv_writer = csv.writer(f)
            if str(doc['id']) in target_ids:

                csv_writer.writerow([doc['id'], doc['accept']])