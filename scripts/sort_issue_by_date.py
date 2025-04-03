import csv

import pymongo



c = pymongo.MongoClient('localhost', port=27017)
coll = c['remediation']['github_issues_non_bots']
with open('data_collection/target_issue_ids.csv', 'r') as f, open('data_collection/target_issue_dates.csv', 'w') as wf:
    target_ids = [int(line) for line in f]
    writer = csv.writer(wf)
    for id in target_ids:
        doc = coll.find_one({'id': id})
        id = doc['id']
        date = doc['created_at']

        writer.writerow([id, date])