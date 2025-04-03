import json
import os
from datetime import datetime

import pymongo
from tqdm import tqdm



c = pymongo.MongoClient('localhost', 27017)
issue_coll  = c['remediation']['github_issues_non_bots']
star_coll = c['remediation']['github_repo_stars']
count = 0
for file in tqdm(os.listdir('data_collection/github_issues/')):
    if file.endswith('.json'):
        with open('data_collection/github_issues/'+file) as f:
            data = json.load(f)
            for issue in data:
                if issue['created_at'] >= '2022-01-01':
                    count += 1
print(count)

for doc in issue_coll.find():
    if doc['created_at'] >= datetime.strptime('2022-01-01', "%Y-%m-%d") and doc['user']['type'] =='User':
        repo = doc['html_url'].replace('https://github.com/', '').rsplit('/issues/')[0]
        issue_creator = doc['user']['login']
        comments_users =  [comment['user']['login'] for comment in doc['comments_data']]
        flag = False
        for each_user in comments_users:
            if each_user!=issue_creator:
                flag = True
        if flag:
            star_doc = star_coll.find_one({'repo': repo})
            if star_doc and star_doc['stars'] >= 10000:

                count += 1
                print(count)