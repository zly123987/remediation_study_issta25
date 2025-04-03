import csv
import json
import os
import re

from tqdm import tqdm
import pyperclip

from scripts.process_non_bot import filter_by_star, filter_by_date, filter_by_no_accept
from utils.miscellaneous import extract_json_from_string



def extract_and_save_cve_issues(client, source_collection_name, target_collection_name):
    # Connect to MongoDB (Assuming MongoDB is running on the default host and port)


    # Access the specified database and collections
    db = client['remediation']
    source_collection = db[source_collection_name]
    target_collection = db[target_collection_name]
    target_collection.create_index('id', unique=True)
    # Regular expression pattern for CVE IDs (e.g., CVE-2020-1234)
    cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE)

    # Fetch all documents in the source collection
    documents = source_collection.find()

    # Initialize a list to store documents to be inserted into the target collection
    cve_issues = []

    for doc in documents:
        # Search for CVE IDs in the 'body' of the issue
        cve_matches = cve_pattern.findall(str(doc))

        # cve_matches upper case
        cve_matches = [cve.upper() for cve in cve_matches]
        # If there are matches, create a new document with the original _id and found CVE IDs
        if cve_matches:
            cve_issues.append({
                'id': doc['id'],  # Saving the original 'id' if needed
                'cve_ids': list(set(cve_matches))  # Removing duplicates
            })
            print('insert', len(cve_issues), list(set(cve_matches)))
            target_collection.update_one({'id': doc['id']}, {'$set': {'cve_ids': list(set(cve_matches))}}, upsert=True)

    print(f"Inserted {len(cve_issues)} documents into '{target_collection_name}'.")


def print_cve_issue(client):
    cve_issues_coll = client['remediation']['github_cve_issues']
    issue_collection = client['remediation']['github_issues_non_bots']
    summary_coll = client['remediation']['github_issues_non_bot_summaries']
    cve_related_ids = [doc['id'] for doc in cve_issues_coll.find()]
    issues = list(issue_collection.find({'id': {'$in': cve_related_ids}}).sort({'_id': -1}).batch_size(30))
    for issue in tqdm(issues, desc='Processing Issues'):
        title = issue['title']
        comments = [comment['body'] for comment in issue['comments_data']]
        full_text = 'Title: ' + title + ". Conversations: " + " ".join(comments)
        print(full_text)
        pyperclip.copy(full_text)
        goon = input('continue?')
        if goon == 'y':
            continue
        else:
            break





def summarize_for_cve(client):

    cve_issues_coll = client['remediation']['github_cve_issues']
    summary_coll = client['remediation']['github_issues_non_bot_summaries']
    cve_related_ids = [doc['id'] for doc in cve_issues_coll.find()]
    issues = list(summary_coll.find({'id': {'$in': cve_related_ids}}).sort({'_id': -1}).batch_size(30))

    visited_ids = set()
    with open('data_collection/cve/summaries.csv', 'r') as fr:
        for l in csv.reader(fr):
            visited_ids.add(int(l[0]))

    for issue in tqdm(issues, desc='Processing Issues'):
        title = issue['title']
        id = issue['id']
        if id in visited_ids:
            continue
        summary = issue['summery']
        # print(summary)

        with open('data_collection/cve/categories_cve.csv', 'r') as f:
            taxonomy = []
            for line in csv.reader(f):
                taxonomy.append(line[0].lower())


        print('title:', title)
        print('summary:', summary)
        print('taxonomy:', taxonomy)
        

def summarize_for_issues(client):

    cve_issues_coll = client['remediation']['github_cve_issues']
    summary_coll = client['remediation']['github_issues_non_bot_summaries']
    cve_related_ids = [doc['id'] for doc in cve_issues_coll.find()]
    target_ids = [doc['id'] for doc in summary_coll.find({}, {'id': 1})]
    ids = list(filter_by_star(client, 10000, target_ids))
    print(len(ids), 'issues are over stars')
    ids = filter_by_date(client, ids)
    visited_ids = set()
    if os.path.exists('data_collection/summaries/summaries.csv'):
        with open('data_collection/summaries/summaries.csv', 'r') as fr:
            for l in csv.reader(fr):
                visited_ids.add(int(l[0]))

    issues = list(summary_coll.find({'id': {'$nin': cve_related_ids, "$in": ids, '$nin': list(visited_ids)}}).sort({'_id': 1}).batch_size(30))
    os.makedirs('data_collection/summaries/', exist_ok=True)


    for issue in tqdm(issues, desc='Processing Issues'):
        title = issue['title']
        id = issue['id']
        if id in visited_ids:
            continue
        summary = issue['summery']
        # print(summary)

        with open('data_collection/summaries/categories_all.csv', 'r') as f:
            taxonomy = []
            for line in csv.reader(f):
                taxonomy.append(line[0].lower())

        print('title:', title)
        print('summary:', summary)
        print('taxonomy:', taxonomy)

    