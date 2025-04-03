import csv
import json
import os
import re
from tqdm import tqdm

from utils.miscellaneous import extract_json_from_string




def check_issue_multiple_cve(c):
    cve_coll = c['remediation']['github_cve_issues']
    coll = c['remediation']['github_issues_non_bots']
    processed_id = set()
    with open('data_processed/advisory/ask_remediation.csv', 'r') as f:
        for line in csv.reader(f):
            processed_id.add(int(line[0]))
    with open('data_collection/issue_multiple_cve.csv', 'w') as f:
        write = csv.writer(f)
        for doc in cve_coll.find():
            if doc['id'] in processed_id:
                continue
            cve_ids = doc['cve_ids']
            if len(cve_ids) > 5:
                issue_doc = coll.find_one({'id': doc['id']})
                write.writerow([doc['id'], len(cve_ids), cve_ids, issue_doc['title'], issue_doc['html_url']])



def map_github_issue_with_advisory(c):
    github_cve_issue_collection = c['remediation']['github_cve_issues']
    github_advisory_collection = c['remediation']['github_advisories']
    for issue_doc in github_cve_issue_collection.find():
        issue_id = issue_doc['id']
        cve_ids = issue_doc['cve_ids']
        for cve_id in cve_ids:
            doc = github_advisory_collection.find_one({'cve_id': cve_id})
            if doc:
                advisory_id = doc['ghsa_id']
                github_advisory_collection.update_one({'ghsa_id': advisory_id}, {'$set': {'issue_id': issue_id}})
                break

def extract_remediation_from_advisory(c):
    github_advisory_collection = c['remediation']['github_advisories']
    for doc in github_advisory_collection.find({'issue_id': {'$exists': True}}):
        description = doc['description']
        issue_id = doc['issue_id']
        with open('data_processed/advisory/ask_remediation.csv', 'a') as f:
            csv_writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            csv_writer.writerow([issue_id, description])

def categorize_cve_description_rs(c):
    cve_description_coll = c['remediation']['description']
    cve_coll = c['remediation']['github_cve_issues']
    coll = c['remediation']['github_issues_non_bots']
    processed_id = {}
    with open('data_processed/advisory/ask_remediation.csv', 'r') as f:
        for line in csv.reader(f):
            processed_id[int(line[0])]= [line[2]]
    for doc in cve_coll.find():
        if doc['id'] in processed_id:
            continue
        cve_ids = doc['cve_ids']
        if len(cve_ids) <= 5:

            processed_id[doc['id']] = []
            for cve_id in cve_ids:

                cve_doc = cve_description_coll.find_one({'cve_id': cve_id})
                if cve_doc:
                    processed_id[doc['id']].append(cve_doc['description'])
    print(len(processed_id), 'cve issues are processed')

    issues = []
    for doc in coll.find({'id': {'$in': list(processed_id)}}):
        issues.append(doc)






    visited_ids = set()
    with open('data_processed/advisory/cve_description_rs.csv', 'r') as f:
        for line in csv.reader(f):
            visited_ids.add(int(line[0]))

    os.makedirs('data_processed/advisory/', exist_ok=True)

    for issue in tqdm(issues, desc='Processing Issues'):
        title = issue['title']
        id = issue['id']
        if id in visited_ids:
            continue
        descriptions = processed_id[id]
        if descriptions == ['no remediation'] or descriptions == []:
            with open('data_collection/cve_description_rs.csv', 'a') as fw:
                writer = csv.writer(fw, quoting=csv.QUOTE_ALL)
                writer.writerow([id, title, 'no remediation'])
            continue
        with open('data_processed/advisory/categories.csv', 'r') as f:
            taxonomy = []
            for line in csv.reader(f):
                taxonomy.append(line[0].lower())


def check_advisory_with_cve(c):
    ids = []
    categories = []
    with open('data_processed/advisory/to_be_checked.csv', 'r') as f:
        for line in csv.reader(f):
            ids.append(int(line[0]))
            categories.append(line[1])
    cve_description_coll = c['remediation']['description']
    cve_coll = c['remediation']['github_cve_issues']
    coll = c['remediation']['github_issues_non_bots']
    processed_id = {}
    with open('data_processed/advisory/ask_remediation.csv', 'r') as f:
        for line in csv.reader(f):
            processed_id[int(line[0])] = [line[2].replace('\n', ' ')]
    unique_cves = set()
    for doc in cve_coll.find():
        if doc['id'] in processed_id:
            continue
        cve_ids = doc['cve_ids']
        if len(cve_ids) <= 5:
            unique_cves.update(cve_ids)
            processed_id[doc['id']] = []
            for cve_id in cve_ids:

                cve_doc = cve_description_coll.find_one({'cve_id': cve_id})
                if cve_doc:
                    processed_id[doc['id']].append(cve_doc['description'].replace('\n', ' '))
    print(len(unique_cves), 'unique cves')

    print(len(processed_id), 'cve issues are processed')

    issues = []
    for doc in coll.find({'id': {'$in': list(processed_id)}}):
        issues.append(doc)

    with open('data_processed/advisory/to_be_checked.csv', 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        for index, id in enumerate(ids):
            if id in processed_id:
                writer.writerow([id, categories[index], *processed_id[id]])