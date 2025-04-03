import csv
import json

from tqdm import tqdm



def determine_role(c):
    issue_coll = c['remediation']['github_issues_non_bots']
    target_ids = []
    with open('data_collection/target_issue_ids.csv', 'r') as f:

        for line in csv.reader(f):
            target_ids.append(int(line[0]))
    for id in tqdm(target_ids):
        doc = issue_coll.find_one({'id': id})
        body = doc['body']
        if 'role' in doc:
            continue
        if body is None:
            with open('data_processed/roles.csv', 'a') as f:
                f.write(f"{id},none\n")
            issue_coll.update_one({'id': id}, {'$set': {'role': 'none'}})
            continue



        print(body)

