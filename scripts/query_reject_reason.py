import csv
import json
import os

from tqdm import tqdm



def query_reject_reason(client):
    issue_coll = client['remediation']['github_issues_non_bots']
    ids = []
    with open('data_processed/acceptance.csv', 'r') as f:
        for line in csv.reader(f):
            if line[1] == 'no':
                ids.append(int(line[0]))
    visited_ids = set()
    if os.path.exists('data_processed/rejected_reasons/reject_reasons.csv'):
        with open('data_processed/rejected_reasons/reject_reasons.csv', 'r') as fr:
            for l in csv.reader(fr, quoting=csv.QUOTE_ALL ):
                visited_ids.add(int(l[0]))


    issues = list(issue_coll.find({'id': {"$in": ids, "$nin": list(visited_ids)}}).sort({'_id': 1}).batch_size(30))


    for issue in tqdm(issues, desc='Query reject reasons'):
        title = issue['title']
        id = issue['id']
        body = issue['body']
        if id in visited_ids:
            continue
        comments = [comment['body'] for comment in issue['comments_data']]
        # if body:
        #     full_text = 'title: '+ title + ". conversations: " + body + ". ".join(comments)
        # else:
        full_text = 'title: '+ title + ". ".join(comments)
        print(full_text)

